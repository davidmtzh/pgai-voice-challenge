import asyncio

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Connect

from app.config import get_settings
from app.realtime_bridge import bridge_twilio_to_openai
from app.scenarios import SCENARIOS

app = FastAPI(title="Pretty Good AI Patient Voice Bot")


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "message": "Pretty Good AI Patient Voice Bot server is running",
    }


@app.post("/voice")
async def voice_webhook(request: Request):
    """
    Twilio calls this endpoint after the outbound call connects.

    Twilio <Stream> URLs do not preserve query string parameters.
    So we pass scenario as a Twilio Stream custom parameter instead.
    """
    settings = get_settings()

    scenario_name = request.query_params.get("scenario", "appointment_basic")

    if scenario_name not in SCENARIOS:
        scenario_name = "appointment_basic"

    response = VoiceResponse()

    connect = Connect()
    stream_url = settings.public_base_url.replace("https://", "wss://").replace("http://", "ws://")

    stream = connect.stream(url=f"{stream_url}/media-stream")
    stream.parameter(name="scenario", value=scenario_name)

    response.append(connect)

    return PlainTextResponse(str(response), media_type="text/xml")


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """
    Twilio Media Stream endpoint.

    Scenario selection is read from Twilio's start.customParameters inside
    the bridge, because Twilio Stream URLs do not support query strings.
    """
    await websocket.accept()
    print("Twilio media stream connected.")

    try:
        await bridge_twilio_to_openai(websocket, scenario_name="appointment_basic")

    except WebSocketDisconnect:
        print("Twilio media stream disconnected.")

    except asyncio.CancelledError:
        print("Media stream task cancelled during server shutdown.")
        return

    except Exception as exc:
        print(f"Media stream error: {exc}")
