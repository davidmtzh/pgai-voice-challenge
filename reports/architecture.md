# Architecture

This project uses Twilio Voice to place outbound calls to the Pretty Good AI assessment line and Twilio Media Streams to send live call audio to a Python FastAPI WebSocket server. The FastAPI server acts as a bridge between Twilio and the OpenAI Realtime API. OpenAI Realtime generates the patient’s spoken responses based on a selected scenario, allowing the bot to have natural two-way conversations with the agent while keeping the implementation simple and focused on voice quality.

I chose this architecture because the challenge prioritizes coherent voice conversations over production-grade infrastructure. Using OpenAI Realtime avoids stitching together separate speech-to-text, LLM, and text-to-speech services, which reduces latency and improves turn-taking. Twilio provides reliable telephony, recording, and call control, while the scenario system makes it easy to run multiple realistic patient tests and compare outcomes across transcripts.
