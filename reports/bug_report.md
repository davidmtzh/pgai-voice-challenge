# Bug Report

This document summarizes quality issues found during automated patient calls to the Pretty Good AI assessment line.

## Testing Summary

The calls were made using a Python voice bot with Twilio Media Streams and OpenAI Realtime. Each call used a realistic patient scenario designed to test medical front-desk voice-agent behavior, including appointment scheduling, insurance questions, noisy caller conditions, third-party caregiver scheduling, and workflow interruptions.

**Evidence included:**
- Audio recordings: `calls/recordings/`
- Transcripts: `calls/transcripts/`
- Call index: `calls/call_index.md`

## Severity Guide

- **High:** Blocks appointment completion, prevents identity verification, creates safety risk, or causes a major workflow failure.
- **Medium:** Causes confusion, breaks character, forces transfer, or creates significant friction but may still allow recovery.
- **Low:** Minor voice-quality, wording, or pacing issue that does not block the workflow.

---

## Bug 01 — Agent breaks character with robotic high-speed voice during scheduling

**Severity:** Medium  
**Scenario:** `insurance_question`  
**Recording:** `calls/recordings/06_insurance_question.mp3`  
**Transcript:** `calls/transcripts/06_insurance_question.txt`  
**Timestamp:** 1:49

### What happened

During the insurance question scenario, the caller moved from asking about insurance to trying to schedule an appointment. Instead of continuing naturally in the same receptionist-style voice, the agent responded with “one moment” in a noticeably robotic, high-speed voice. The tone and pacing changed abruptly and broke the character of the front-desk assistant.

### Expected behavior

The agent should stay in the same natural voice and continue the scheduling workflow clearly. It should either ask for appointment details, explain that it is checking availability, or clearly state that it is transferring the caller while maintaining a consistent tone and pace.

### Why this matters

This breaks the illusion of a natural medical front-desk assistant and may confuse or frustrate patients. It also suggests the agent may be failing or falling back during an important workflow transition from insurance verification to appointment scheduling.

### Evidence

At approximately 1:49 in the `insurance_question` recording, after the caller asks to schedule, the agent says “one moment” in a robotic, high-speed voice instead of staying in character.

---

## Bug 02 — Agent interrupts patient during date-of-birth collection and fails to complete appointment

**Severity:** High  
**Scenario:** `noisy_caller`  
**Recording:** `calls/recordings/07_noisy_caller.mp3`  
**Transcript:** `calls/transcripts/07_noisy_caller.txt`  
**Timestamp:** 0:26

### What happened

During the noisy caller scenario, the agent asked the caller for their date of birth. The caller began answering with something like, “Sure, my birthdate is December...,” but the agent interrupted before the caller finished. After interrupting, the agent became fixated on asking for the date of birth again and lost normal turn-taking. The conversation did not recover properly, and the agent was not able to complete the appointment scheduling flow.

### Expected behavior

The agent should wait for the caller to finish giving their full date of birth before responding. If the audio was unclear, the agent should ask for clarification after the caller finishes, not interrupt mid-answer. The agent should avoid repeatedly asking for the same information when the caller is already trying to provide it.

### Why this matters

Date of birth is a required identity-verification detail in a medical office workflow. Interrupting the patient during this step prevents verification, breaks natural turn-taking, and can block the scheduling process. Since the appointment was not completed, this becomes a high-impact workflow failure.

### Evidence

At approximately 0:26 in the `noisy_caller` recording, the agent asks for the caller’s date of birth. The caller starts to answer, “Sure, my birthdate is December...,” but the agent interrupts before the answer is complete. After that, the agent repeatedly returns to the date-of-birth request and fails to complete the appointment.

---

## Bug 03 — Agent interrupts third-party caller during patient DOB collection and gets stuck

**Severity:** High  
**Scenario:** `third_party_caregiver`  
**Recording:** `calls/recordings/05_third_party_caregiver_run_01_dob_loop.mp3`  
**Transcript:** `calls/transcripts/05_third_party_caregiver_run_01_dob_loop.txt`  
**Timestamp:** 0:28

### What happened

During the third-party caregiver scenario, the caller was calling on behalf of his mother, Lucia Martinez. The agent asked whether it was speaking with Carlos, but the caller moved into explaining that he was calling for his mom. The agent then asked for the patient’s full name and date of birth. The caller began providing the patient’s name and date of birth, but the agent interrupted before the caller finished. After that, the agent became stuck asking for the birthdate instead of allowing the caller to complete the answer.

### Expected behavior

The agent should clearly distinguish between the caller and the patient, then allow the caller to finish providing the patient’s full name and date of birth. If the answer is unclear, the agent should ask for clarification after the caller finishes speaking, not interrupt mid-answer. The agent should also avoid repeatedly asking for the same information when the caller is already trying to provide it.

### Why this matters

Third-party scheduling is common in medical offices, especially when an adult child helps a parent schedule care. The agent needs to manage caller identity, patient identity, authorization, and basic verification details. Interrupting during date-of-birth collection prevents verification and blocks the scheduling workflow.

### Evidence

At approximately 0:28 in the first `third_party_caregiver` recording, the agent asks for the patient’s full name and date of birth. The caller begins to provide Lucia Martinez’s information, but the agent interrupts before the date of birth is completed and becomes stuck asking for the birthdate. This issue is clearest in the audio recording because the voices overlap.

---

## Bug 04 — Agent unable to complete third-party scheduling after verifying patient information

**Severity:** Medium  
**Scenario:** `third_party_caregiver`  
**Recording:** `calls/recordings/06_third_party_caregiver_run_02_dob_loop.mp3`  
**Transcript:** `calls/transcripts/06_third_party_caregiver_run_02_dob_loop.txt`  
**Timestamp:** 1:30

### What happened

During a second run of the third-party caregiver scenario, the agent correctly collected and recognized the patient’s date of birth. After the caller confirmed the requested information, the agent stated that it was not able to proceed and transferred the caller to another department instead of completing the appointment scheduling flow.

### Expected behavior

After collecting the caller and patient information, the agent should either continue scheduling the appointment, clearly explain what additional information or authorization is required, or provide a specific reason why a transfer is necessary. If a transfer is required, the agent should explain why and confirm that the receiving department can help with the appointment.

### Why this matters

Third-party scheduling is a common medical office workflow, especially when adult children help parents schedule care. If the agent collects the correct patient information but still cannot proceed, the caller may be forced into a transfer loop or have to repeat the same information to another department. This creates friction and may prevent successful appointment completion.

### Evidence

At approximately 1:30 in the second `third_party_caregiver` run, the agent correctly recognized the birthdate but then said it was unable to proceed and transferred the caller instead of completing the appointment scheduling flow.

