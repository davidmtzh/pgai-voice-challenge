# Pretty Good AI Patient Voice Bot

This project builds an automated AI patient that calls the Pretty Good AI assessment test line, has realistic phone conversations with their AI agent, records the calls, transcribes them, and analyzes the transcripts for bugs and quality issues.

## Goal

The goal is to test the quality, safety, and reliability of a medical voice agent through realistic patient scenarios such as appointment scheduling, rescheduling, medication refills, office questions, insurance questions, and edge cases.

## Architecture

Twilio places the outbound phone call and streams live call audio to a Python FastAPI server using Twilio Media Streams. The FastAPI app bridges that audio to the OpenAI Realtime API, which acts as the patient and generates natural spoken responses. After each call, recordings and transcripts are saved for review and bug reporting.

## Setup

1. Clone the repository.
2. Create a Python virtual environment.
3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Copy `.env.example` to `.env`.
5. Add your OpenAI and Twilio credentials.
6. Start the FastAPI server.
7. Start ngrok.
8. Run a call scenario.

## Required Environment Variables

See `.env.example`.

## Run

Coming soon.

## Deliverables

- Working Python voice bot
- 10 call recordings
- 10 call transcripts
- Bug report
- Architecture document
- Loom walkthrough
