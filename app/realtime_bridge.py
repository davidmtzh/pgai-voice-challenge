import asyncio
import base64
import json
import audioop
from typing import Optional

import websockets
from fastapi import WebSocket

from app.config import get_settings
from app.scenarios import SCENARIOS, build_patient_prompt


OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime"

OPENAI_PCM_SAMPLE_RATE = 24000
TWILIO_SAMPLE_RATE = 8000


def pcm16_base64_to_twilio_mulaw_base64(pcm16_b64: str) -> str:
    """
    Convert OpenAI PCM16 base64 audio into Twilio-compatible μ-law 8kHz base64 audio.
    """
    pcm16_audio = base64.b64decode(pcm16_b64)

    pcm16_8khz, _ = audioop.ratecv(
        pcm16_audio,
        2,
        1,
        OPENAI_PCM_SAMPLE_RATE,
        TWILIO_SAMPLE_RATE,
        None,
    )

    mulaw_audio = audioop.lin2ulaw(pcm16_8khz, 2)

    return base64.b64encode(mulaw_audio).decode("utf-8")


async def bridge_twilio_to_openai(
    twilio_ws: WebSocket,
    scenario_name: str = "appointment_basic",
) -> None:
    """
    Bridges Twilio Media Streams audio to OpenAI Realtime.

    The selected scenario is received from Twilio's start.customParameters.
    """
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env")

    model = settings.openai_realtime_model or "gpt-realtime"
    openai_url = f"{OPENAI_REALTIME_URL}?model={model}"

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
    }

    stream_sid: Optional[str] = None
    audio_chunks_sent = 0
    assistant_speaking = False
    openai_session_initialized = False

    async with websockets.connect(
        openai_url,
        additional_headers=headers,
        ping_interval=20,
        ping_timeout=20,
        max_size=None,
    ) as openai_ws:
        print("Connected to OpenAI Realtime.")

        async def initialize_for_scenario(selected_scenario: str) -> None:
            nonlocal openai_session_initialized

            if selected_scenario not in SCENARIOS:
                print(f"Unknown scenario '{selected_scenario}', falling back to appointment_basic.")
                selected_scenario = "appointment_basic"

            print(f"Using scenario: {selected_scenario}")

            prompt = build_patient_prompt(selected_scenario)

            print("=" * 80)
            print(f"Building OpenAI prompt for scenario: {selected_scenario}")
            print(prompt[:1200])
            print("=" * 80)

            await initialize_openai_session(openai_ws, prompt)
            openai_session_initialized = True

        async def receive_from_twilio() -> None:
            nonlocal stream_sid

            try:
                while True:
                    message = await twilio_ws.receive_text()
                    data = json.loads(message)
                    event_type = data.get("event")

                    if event_type == "connected":
                        print("Twilio event: connected")

                    elif event_type == "start":
                        stream_sid = data["start"]["streamSid"]
                        call_sid = data["start"].get("callSid")
                        media_format = data["start"].get("mediaFormat", {})
                        custom_parameters = data["start"].get("customParameters", {})

                        selected_scenario = custom_parameters.get("scenario", scenario_name)

                        print(f"Twilio stream started. Stream SID: {stream_sid}")
                        print(f"Twilio Call SID: {call_sid}")
                        print(f"Twilio media format: {media_format}")
                        print(f"Twilio custom parameters: {custom_parameters}")

                        await initialize_for_scenario(selected_scenario)

                    elif event_type == "media":
                        if not openai_session_initialized:
                            continue

                        audio_payload = data["media"]["payload"]

                        await openai_ws.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": audio_payload,
                        }))

                    elif event_type == "mark":
                        mark_name = data.get("mark", {}).get("name")
                        print(f"Twilio mark received: {mark_name}")

                    elif event_type == "stop":
                        print("Twilio stream stopped.")
                        break

            except Exception as exc:
                print(f"Twilio receive loop ended: {exc}")

        async def send_to_twilio() -> None:
            nonlocal audio_chunks_sent, assistant_speaking

            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    response_type = response.get("type")

                    if response_type in {
                        "session.created",
                        "session.updated",
                        "response.created",
                        "response.done",
                        "response.output_audio.delta",
                        "response.output_audio.done",
                        "response.output_audio_transcript.delta",
                        "input_audio_buffer.speech_started",
                        "input_audio_buffer.speech_stopped",
                        "error",
                    }:
                        print(f"OpenAI event: {response_type}")

                    if response_type == "session.updated":
                        print("OpenAI session updated successfully.")

                    elif response_type == "error":
                        print("OpenAI error:", json.dumps(response, indent=2))
                        continue

                    elif response_type == "response.created":
                        assistant_speaking = True

                    elif response_type == "response.done":
                        assistant_speaking = False

                    elif response_type == "input_audio_buffer.speech_started":
                        if stream_sid and assistant_speaking:
                            print("Agent interrupted. Clearing queued Twilio audio.")
                            await twilio_ws.send_json({
                                "event": "clear",
                                "streamSid": stream_sid,
                            })

                    elif response_type == "response.output_audio.delta":
                        audio_delta = response.get("delta")

                        if not audio_delta:
                            continue

                        if not stream_sid:
                            print("Received OpenAI audio before Twilio streamSid was ready.")
                            continue

                        try:
                            twilio_audio_b64 = pcm16_base64_to_twilio_mulaw_base64(audio_delta)
                        except Exception as exc:
                            print(f"Audio conversion failed: {exc}")
                            continue

                        audio_chunks_sent += 1

                        print(
                            "Sending converted audio to Twilio. "
                            f"chunk={audio_chunks_sent}, base64_chars={len(twilio_audio_b64)}"
                        )

                        await twilio_ws.send_json({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": twilio_audio_b64,
                            },
                        })

                        await twilio_ws.send_json({
                            "event": "mark",
                            "streamSid": stream_sid,
                            "mark": {
                                "name": f"converted-openai-audio-{audio_chunks_sent}",
                            },
                        })

            except Exception as exc:
                print(f"OpenAI send loop ended: {exc}")

        await asyncio.gather(receive_from_twilio(), send_to_twilio())


async def initialize_openai_session(openai_ws, prompt: str) -> None:
    """
    Configure Realtime session using the current schema your project accepts.
    """
    session_update = {
        "type": "session.update",
        "session": {
            "type": "realtime",
            "instructions": prompt,
            "output_modalities": ["audio"],
            "audio": {
                "input": {
                    "format": {
                        "type": "audio/pcmu"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.55,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 700,
                        "create_response": True,
                        "interrupt_response": True
                    }
                },
                "output": {
                    "format": {
                        "type": "audio/pcm",
                        "rate": 24000
                    },
                    "voice": "alloy"
                }
            }
        },
    }

    await openai_ws.send(json.dumps(session_update))
