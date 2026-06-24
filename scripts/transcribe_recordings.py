import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from app.config import get_settings


SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".ogg"}

def make_readable_transcript(text: str) -> str:
    """
    Makes plain transcription text easier to review in GitHub.

    This does not add speaker labels. It only improves readability by
    adding line breaks after sentence endings.
    """
    text = " ".join(text.split())

    sentence_endings = [". ", "? ", "! "]

    for ending in sentence_endings:
        text = text.replace(ending, ending + "\n")

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    return "\n".join(lines)

def transcribe_audio_file(audio_path: Path, output_dir: Path, metadata_dir: Path, model: str) -> Path:
    """
    Transcribes one audio file and saves:
    - transcript text to calls/transcripts/<audio_name>.txt
    - metadata JSON to calls/metadata/<audio_name>.json
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if audio_path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        raise ValueError(f"Unsupported audio file type: {audio_path.suffix}")

    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env")

    client = OpenAI(api_key=settings.openai_api_key)

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    transcript_path = output_dir / f"{audio_path.stem}.txt"
    metadata_path = metadata_dir / f"{audio_path.stem}.json"

    print(f"Transcribing: {audio_path}")
    print(f"Model: {model}")

    transcription_prompt = (
        "This is a phone call between a medical office AI agent and a realistic patient caller. "
        "Preserve natural wording, short responses, filler words like 'um' or 'I think' when present, "
        "and medical scheduling details such as appointment times, insurance, medication names, and symptoms."
    )

    with audio_path.open("rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="text",
            prompt=transcription_prompt,
        )

    if isinstance(transcription, str):
        transcript_text = transcription
    else:
        transcript_text = getattr(transcription, "text", str(transcription))

    transcript_text = transcript_text.strip()

    readable_text = make_readable_transcript(transcript_text)
    transcript_path.write_text(readable_text + "\n", encoding="utf-8")

    metadata = {
        "audio_file": str(audio_path),
        "transcript_file": str(transcript_path),
        "model": model,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "characters": len(transcript_text),
        "words_estimate": len(transcript_text.split()),
    }

    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved transcript: {transcript_path}")
    print(f"Saved metadata: {metadata_path}")

    return transcript_path


def find_audio_files(recordings_dir: Path) -> list[Path]:
    if not recordings_dir.exists():
        return []

    audio_files = [
        path
        for path in recordings_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS
    ]

    return sorted(audio_files)


def main() -> None:
    load_dotenv()

    settings = get_settings()

    parser = argparse.ArgumentParser(
        description="Transcribe Twilio call recordings using OpenAI speech-to-text."
    )

    parser.add_argument(
        "--file",
        type=Path,
        help="Path to one audio file to transcribe.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Transcribe all audio files inside calls/recordings.",
    )

    parser.add_argument(
        "--recordings-dir",
        type=Path,
        default=Path("calls/recordings"),
        help="Directory containing Twilio MP3 recordings.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("calls/transcripts"),
        help="Directory where transcript .txt files will be saved.",
    )

    parser.add_argument(
        "--metadata-dir",
        type=Path,
        default=Path("calls/metadata"),
        help="Directory where transcript metadata .json files will be saved.",
    )

    parser.add_argument(
        "--model",
        default=getattr(settings, "transcription_model", None) or "gpt-4o-mini-transcribe",
        help="OpenAI transcription model to use.",
    )

    args = parser.parse_args()

    if not args.file and not args.all:
        raise SystemExit("Choose either --file <path> or --all")

    if args.file and args.all:
        raise SystemExit("Use either --file or --all, not both.")

    if args.file:
        transcribe_audio_file(
            audio_path=args.file,
            output_dir=args.output_dir,
            metadata_dir=args.metadata_dir,
            model=args.model,
        )
        return

    audio_files = find_audio_files(args.recordings_dir)

    if not audio_files:
        raise SystemExit(f"No supported audio files found in {args.recordings_dir}")

    print(f"Found {len(audio_files)} audio file(s).")

    for audio_path in audio_files:
        transcribe_audio_file(
            audio_path=audio_path,
            output_dir=args.output_dir,
            metadata_dir=args.metadata_dir,
            model=args.model,
        )


if __name__ == "__main__":
    main()
