import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_realtime_model: str
    transcription_model: str

    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str

    public_base_url: str
    pgai_test_number: str


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_realtime_model=os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime"),
        transcription_model=os.getenv("TRANSCRIPTION_MODEL", "whisper-1"),
        twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
        twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
        twilio_from_number=os.getenv("TWILIO_FROM_NUMBER", ""),
        public_base_url=os.getenv("PUBLIC_BASE_URL", ""),
        pgai_test_number=os.getenv("PGAI_TEST_NUMBER", "+18054398008"),
    )
