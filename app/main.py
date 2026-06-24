from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Connect

from app.config import get_settings
from app.realtime_bridge import bridge_twilio_to_openai

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

    It returns TwiML that connects the phone call audio to our WebSocket.
    """
    settings = get_settings()

    response = VoiceResponse()

    connect = Connect()
    stream_url = settings.public_base_url.replace("https://", "wss://").replace("http://", "ws://")
    connect.stream(url=f"{stream_url}/media-stream")

    response.append(connect)

    return PlainTextResponse(str(response), media_type="text/xml")


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """
    Twilio Media Stream endpoint.

    Phase 3: bridge Twilio audio to OpenAI Realtime and stream OpenAI audio
    back into the phone call.
    """
    await websocket.accept()
    print("Twilio media stream connected.")

    try:
        await bridge_twilio_to_openai(websocket, scenario_name="appointment_basic")
    except WebSocketDisconnect:
        print("Twilio media stream disconnected.")
    except Exception as exc:
        print(f"Media stream error: {exc}")
