# Iteration Log

This document tracks the main improvements made while building and testing the automated patient voice bot for the Pretty Good AI assessment line.

## Attempt 1 — Twilio connection test

**Observation:**  
The first goal was to confirm that the Python script could place an outbound call through Twilio to the assessment number. The call connected successfully, and the FastAPI server received Twilio Media Stream events.

**Change made:**  
Added the initial Twilio outbound call flow, FastAPI `/voice` route, and `/media-stream` WebSocket endpoint.

**Result:**  
The phone call connected and Twilio successfully reached the local FastAPI server through ngrok.

---

## Attempt 2 — OpenAI Realtime bridge

**Observation:**  
The call was connected, but the bot was not yet producing live patient responses.

**Change made:**  
Added the OpenAI Realtime WebSocket bridge so the FastAPI server could forward Twilio call audio to OpenAI and stream OpenAI's audio response back into the call.

**Result:**  
Twilio and OpenAI Realtime connected successfully, but the first generated audio responses were not clearly audible.

---

## Attempt 3 — Audio format issue

**Observation:**  
Early recordings contained the Pretty Good AI agent's voice plus static or unclear patient audio. This suggested that the audio format being sent back to Twilio was not compatible.

**Change made:**  
Changed the OpenAI output audio format and added audio conversion from OpenAI PCM audio to Twilio-compatible 8kHz G.711 μ-law audio.

**Result:**  
The patient bot became audible in the phone recording, and the live call started working as an actual two-way voice conversation.

---

## Attempt 4 — Turn-taking issue

**Observation:**  
The patient bot sometimes started speaking too early and overlapped with the Pretty Good AI agent’s greeting.

**Change made:**  
Removed the forced initial greeting and relied on voice activity detection so the patient bot would wait until the office agent finished speaking before responding.

**Result:**  
The bot responded more naturally, reduced overlap, and improved the overall conversation flow.

---

## Attempt 5 — Scenario selection and patient realism

**Observation:**  
The early bot worked technically, but the conversations needed more realistic patient behavior and more diverse test cases.

**Change made:**  
Added scenario-based prompts in `app/scenarios.py`, including appointment scheduling, insurance questions, location questions, urgent symptoms, medication refill edge cases, noisy caller behavior, cancellation, rescheduling, and third-party caregiver scheduling.

**Result:**  
The bot could run different patient scenarios using commands like `python -m scripts.run_call --scenario noisy_caller`, making the testing process repeatable and easier to evaluate.

---

## Attempt 6 — Natural speech and hold behavior

**Observation:**  
In some early calls, the patient bot sounded too neutral and sometimes responded during hold music, beeps, or automated messages.

**Change made:**  
Improved the prompt rules for natural patient speech, pauses, filler language, frustration, urgency, and hold behavior. Added instructions for the bot to stay quiet during hold music, beeps, and recorded messages, then resume only when a human-like agent returned.

**Result:**  
The calls sounded more realistic and closer to how an actual patient would behave during a medical office phone call.

---

## Attempt 7 — Repeated-question and stuck-loop handling

**Observation:**  
During some calls, the Pretty Good AI agent got stuck asking for the same information, especially date of birth. The patient bot was too calm and continued repeating information without showing frustration.

**Change made:**  
Added stuck-loop recovery rules. If the agent interrupts, repeats the same question, or fails to understand after multiple attempts, the patient bot now pushes back naturally and asks for a real person.

**Result:**  
The bot became better at exposing workflow failures because it reacted more like a real patient when the agent got stuck.

---

## Attempt 8 — Final evidence calls and bug report

**Observation:**  
After the technical bridge and prompts were stable, I ran final evidence calls across the selected scenarios and reviewed the recordings.

**Change made:**  
Saved final audio recordings in `calls/recordings/`, generated transcripts in `calls/transcripts/`, created a call index, and documented the main issues in `reports/bug_report.md`.

**Result:**  
The final submission includes working Python code, repeatable scenarios, audio recordings, transcripts, and a bug report with evidence for issues such as DOB interruption loops, failure to complete third-party scheduling, and robotic voice fallback during scheduling.
