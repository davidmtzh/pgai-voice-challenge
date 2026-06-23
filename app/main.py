from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

from app.config import get_settings

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

    For Phase 2, this returns TwiML that connects the phone call audio
    to our /media-stream WebSocket. In Phase 3, that WebSocket will bridge
    Twilio audio to OpenAI Realtime.
    """
    settings = get_settings()

    response = VoiceResponse()

    response.say(
        "Hello. This is the automated patient simulator connecting now.",
        voice="alice",
        language="en-US",
    )

    connect = Connect()
    stream_url = settings.public_base_url.replace("https://", "wss://").replace("http://", "ws://")
    connect.stream(url=f"{stream_url}/media-stream")

    response.append(connect)

    return PlainTextResponse(str(response), media_type="text/xml")


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """
    Phase 2 WebSocket endpoint.

    For now, we only accept the stream and print incoming Twilio events.
    In Phase 3, this becomes the Twilio <-> OpenAI Realtime bridge.
    """
    await websocket.accept()
    print("Twilio media stream connected.")

    try:
        while True:
            message = await websocket.receive_text()
            print("Received Twilio event:", message[:300])
    except WebSocketDisconnect:
        print("Twilio media stream disconnected.")
