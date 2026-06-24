from twilio.rest import Client

from app.config import get_settings


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


def place_assessment_call() -> str:
    """
    Places one outbound call to the Pretty Good AI assessment number.

    Safety rule:
    The destination is read from PGAI_TEST_NUMBER and must match the required
    assessment number. This prevents accidentally calling other numbers.
    """
    validate_required_settings()
    settings = get_settings()

    required_number = "+18054398008"

    if settings.pgai_test_number != required_number:
        raise RuntimeError(
            f"Safety check failed. PGAI_TEST_NUMBER must be {required_number}, "
            f"but got {settings.pgai_test_number}"
        )

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    call = client.calls.create(
        to=settings.pgai_test_number,
        from_=settings.twilio_from_number,
        url=f"{settings.public_base_url}/voice",
        record=True,
        time_limit=settings.max_call_duration_seconds,
    )

    return call.sid
