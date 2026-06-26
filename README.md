# Pretty Good AI Patient Voice Bot

This project builds an automated AI patient that calls the Pretty Good AI assessment test line, has realistic phone conversations with their AI agent, records the calls, transcribes them, and documents bugs and quality issues found during testing.

The bot was built for the Pretty Good AI AI Engineering Challenge. It is designed to test medical front-desk voice-agent behavior across realistic patient scenarios such as appointment scheduling, rescheduling, medication refill requests, insurance questions, location questions, noisy callers, urgent symptoms, frustrated callers, and third-party caregiver calls.

## Goal

The goal is to test the quality, safety, reliability, and conversation flow of a medical voice agent using repeatable automated phone calls.

The system evaluates whether the agent can:

- Maintain natural turn-taking
- Handle realistic patient requests
- Avoid interrupting callers during important information collection
- Complete appointment-related workflows
- Escalate or transfer appropriately
- Stay understandable and natural during live voice calls

## Architecture

This project uses Twilio Voice to place outbound calls to the Pretty Good AI assessment line. Twilio Media Streams sends live call audio to a Python FastAPI WebSocket server. The FastAPI server acts as a bridge between Twilio and the OpenAI Realtime API.

OpenAI Realtime generates the patient’s spoken responses based on the selected scenario. The FastAPI bridge receives audio from Twilio, forwards it to OpenAI Realtime, receives generated patient audio, converts it to Twilio-compatible 8kHz G.711 μ-law audio, and streams it back into the live call.

During local development, ngrok is used to expose the local FastAPI server to the public internet so Twilio can reach the `/voice` and `/media-stream` endpoints. In a production version, the FastAPI server could be deployed to Railway, Azure, Render, AWS, or another cloud backend instead of using ngrok.

## Project Structure

~~~text
app/
  caller.py                 # Places outbound Twilio calls
  config.py                 # Loads environment variables
  main.py                   # FastAPI routes and WebSocket endpoint
  realtime_bridge.py        # Twilio <-> OpenAI Realtime audio bridge
  scenarios.py              # Patient scenarios and prompt rules

scripts/
  run_call.py               # Runs a selected call scenario
  transcribe_recordings.py  # Transcribes saved call recordings

calls/
  recordings/               # Final call audio evidence
  transcripts/              # Transcripts generated from recordings
  metadata/                 # Optional call metadata
  call_index.md             # Maps calls to scenarios and evidence files

reports/
  architecture.md           # Architecture explanation
  bug_report.md             # Bugs and quality issues found
  iteration_log.md          # Development and testing improvements
~~~

## Setup

Clone the repository:

~~~bash
git clone <repo-url>
cd pgai-voice-challenge
~~~

Create and activate a Python virtual environment:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

Install dependencies:

~~~bash
pip install -r requirements.txt
~~~

Copy the example environment file:

~~~bash
cp .env.example .env
~~~

Add your Twilio and OpenAI credentials to `.env`.

Do not commit `.env` to GitHub.

## Required Environment Variables

See `.env.example` for the full list.

The main environment variables are:

~~~text
OPENAI_API_KEY=
OPENAI_REALTIME_MODEL=
TRANSCRIPTION_MODEL=

TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=

PUBLIC_BASE_URL=
PGAI_TEST_NUMBER=

MAX_CALLS=
MAX_CALL_DURATION_SECONDS=
~~~

## Running the FastAPI Server

Start the FastAPI server locally:

~~~bash
uvicorn app.main:app --host 0.0.0.0 --port 5050 --reload
~~~

In a second terminal, start ngrok:

~~~bash
ngrok http 5050
~~~

Copy the public ngrok HTTPS URL and update `PUBLIC_BASE_URL` in `.env`.

Example:

~~~env
PUBLIC_BASE_URL=https://your-ngrok-url.ngrok-free.app
~~~

Restart the FastAPI server after updating `.env`.

## Running a Call Scenario

Use the scenario runner:

~~~bash
python -m scripts.run_call --scenario noisy_caller
~~~

Example scenarios:

~~~bash
python -m scripts.run_call --scenario interrupting_complaint_caller
python -m scripts.run_call --scenario frustrated_hold_disconnect
python -m scripts.run_call --scenario urgent_symptom_triage
python -m scripts.run_call --scenario controlled_medication_edge_case
python -m scripts.run_call --scenario third_party_caregiver
python -m scripts.run_call --scenario reschedule_appointment
python -m scripts.run_call --scenario noisy_caller
python -m scripts.run_call --scenario insurance_question
python -m scripts.run_call --scenario location_question
python -m scripts.run_call --scenario cancel_appointment
~~~

Each call is placed through Twilio and recorded for later review.

## Transcribing Recordings

To transcribe all saved recordings:

~~~bash
python -m scripts.transcribe_recordings --all
~~~

To transcribe one recording:

~~~bash
python -m scripts.transcribe_recordings --file calls/recordings/09_insurance_question.mp3
~~~

Transcripts are saved in:

~~~text
calls/transcripts/
~~~

## Final Evidence

Final evidence is organized in:

~~~text
calls/recordings/
calls/transcripts/
calls/call_index.md
reports/bug_report.md
reports/architecture.md
reports/iteration_log.md
~~~

The call index maps each scenario to its audio recording, transcript, and testing focus.

## Calls Included

This repository includes more than 10 completed assessment calls. The final evidence set includes scenarios such as:

- Interrupting complaint caller
- Frustrated hold/disconnect caller
- Urgent symptom triage
- Controlled medication refill edge case
- Third-party caregiver scheduling
- Noisy caller
- Rescheduling appointment
- Insurance question
- Location question
- Cancel appointment

## Bugs Found

The bug report documents issues found during automated calls, including:

- Agent interrupting caller during date-of-birth collection
- Agent getting stuck repeatedly asking for the same information
- Agent failing to complete appointment scheduling
- Third-party caregiver scheduling limitations
- Robotic high-speed voice fallback during scheduling

See:

~~~text
reports/bug_report.md
~~~

## Iteration Summary

The project went through multiple iterations:

- Confirmed Twilio outbound calling and Media Stream connection
- Added OpenAI Realtime WebSocket bridge
- Fixed audio format conversion so the patient voice was audible
- Improved turn-taking by removing forced greetings
- Added scenario-based patient behavior
- Added hold behavior and automated-message handling
- Added stuck-loop escalation behavior
- Generated final recordings, transcripts, call index, and bug report

See:

~~~text
reports/iteration_log.md
~~~

## Deliverables

This repository includes:

- Working Python voice bot
- FastAPI WebSocket server
- Twilio outbound calling flow
- OpenAI Realtime voice bridge
- Scenario-based patient prompts
- Final call recordings
- Final call transcripts
- Call index
- Bug report
- Architecture document
- Iteration log
- Loom walkthrough video

## Notes

The project uses ngrok for local development so Twilio can reach the local FastAPI server. For production, the FastAPI app should be deployed to a stable cloud backend such as Railway, Azure, Render, AWS, or another hosted environment.

Secrets are loaded through `.env` and should not be committed to GitHub.
