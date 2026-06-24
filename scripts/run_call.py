import argparse

from app.caller import place_assessment_call
from app.scenarios import SCENARIOS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Start one Pretty Good AI assessment call."
    )

    parser.add_argument(
        "--scenario",
        default="appointment_basic",
        choices=sorted(SCENARIOS.keys()),
        help="Scenario name to run.",
    )

    args = parser.parse_args()

    call_sid = place_assessment_call(scenario_name=args.scenario)

    print(f"Started assessment call.")
    print(f"Scenario: {args.scenario}")
    print(f"Twilio Call SID: {call_sid}")


if __name__ == "__main__":
    main()
