from app.caller import place_assessment_call


if __name__ == "__main__":
    call_sid = place_assessment_call()
    print(f"Started assessment call. Twilio Call SID: {call_sid}")
