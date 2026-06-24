# Iteration Log

This document tracks improvements made after listening to early test calls.

## Attempt 1

**Observation:** Initial call behavior pending.  
**Change made:** Pending.  
**Result:** Pending.

## Attempt 2

**Observation:** Pending.  
**Change made:** Pending.  
**Result:** Pending.

## Attempt 3

**Observation:** Pending.  
**Change made:** Pending.  
**Result:** Pending.

## Attempt 1 — Twilio connection test

**Observation:** The initial Twilio call connected successfully and the FastAPI server received Media Stream events, but the bot was not yet connected to OpenAI Realtime.  
**Change made:** Added the OpenAI Realtime WebSocket bridge.  
**Result:** Twilio and OpenAI connected, but the first audio responses were not audible.

## Attempt 2 — Audio format issue

**Observation:** The Twilio recording contained Pretty Good AI's voice plus static instead of a clean patient voice.  
**Change made:** Switched OpenAI output to PCM audio and converted it to Twilio-compatible 8kHz G.711 μ-law audio before sending it back to Twilio.  
**Result:** The patient bot became audible in the recording.

## Attempt 3 — Turn-taking issue

**Observation:** The patient bot started speaking too early and overlapped with Pretty Good AI's greeting.  
**Change made:** Removed the forced greeting and allowed OpenAI server-side voice activity detection to respond after the agent stopped speaking.  
**Result:** The patient bot responded more naturally and the conversation flow improved.

## Prompt polish — natural patient behavior

Increased test call duration to 90 seconds to evaluate longer turn-taking and follow-up handling. The caller sounded more natural, accepted new information from the office agent, and used common patient-like wording. Added stronger behavior rules for urgency, uncertainty, third-party calling, and hold situations so the caller waits silently during hold music or beeping and resumes only when a human voice returns.


## 90-second scenario tests

Ran 90-second test calls for multiple scenarios after adding stronger patient prompts, edge-case behavior, natural filler language, and hold behavior rules. The calls sounded natural, the caller accepted new information properly, and the dialogue felt more realistic across different scenarios. This version was selected as the stable prompt version for final evidence collection.

