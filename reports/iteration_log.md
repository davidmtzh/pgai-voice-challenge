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
