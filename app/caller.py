from urllib.parse import urlencode

from twilio.rest import Client

from app.config import get_settings


REQUIRED_ASSESSMENT_NUMBER = "+18054398008"


def validate_required_settings() -> None:
    settings = get_settings()

    missing = []

    if not settings.twilio_account_sid:
        missing.append("TWILIO_ACCOUNT_SID")
    if not settings.twilio_auth_token:
        missing.append("TWILIO_AUTH_TOKEN")
    if not settings.twilio_from_number:
        missing.append("TWILIO_FROM_NUMBER")
    if not settings.public_base_url:
        missing.append("PUBLIC_BASE_URL")

    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )


def place_assessment_call(scenario_name: str = "appointment_basic") -> str:
    """
    Places one outbound call to the Pretty Good AI assessment number.

    Safety rule:
    The destination must be the required assessment number.
    """
    validate_required_settings()
    settings = get_settings()

    if settings.pgai_test_number != REQUIRED_ASSESSMENT_NUMBER:
        raise RuntimeError(
            f"Safety check failed. PGAI_TEST_NUMBER must be {REQUIRED_ASSESSMENT_NUMBER}, "
            f"but got {settings.pgai_test_number}"
        )

    query = urlencode({"scenario": scenario_name})
    voice_url = f"{settings.public_base_url}/voice?{query}"

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    call = client.calls.create(
        to=settings.pgai_test_number,
        from_=settings.twilio_from_number,
        url=voice_url,
        record=True,
        time_limit=settings.max_call_duration_seconds,
    )

    return call.sid
