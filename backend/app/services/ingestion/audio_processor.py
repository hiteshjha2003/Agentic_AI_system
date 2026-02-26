# backend/app/services/ingestion/audio_processor.py
from typing import Dict, Any, List, Optional
from app.services.sambanova_client import SambaNovaOrchestrator

class AudioProcessor:
    """
    Process meeting audio using SambaNova's Whisper-Large-v3 (cloud).
    No local FFmpeg or openai-whisper needed anymore.
    """

    def __init__(self):
        self.sambanova = SambaNovaOrchestrator()

    async def process_meeting_audio(
        self,
        audio_bytes: bytes,
        filename: str = "meeting.mp3",
        participants: List[str] = None
    ) -> Dict[str, Any]:
        """
        Full pipeline: SambaNova Whisper → transcription → extract action items.
        """
        participants = participants or []

        # 1. Transcribe with SambaNova Whisper-Large-v3
        transcription_result = await self.sambanova.transcribe_audio(
            audio_bytes=audio_bytes,
            filename=filename,
            language="en",                    # change to None for auto-detect
            prompt="Transcribe accurately, include speaker names if mentioned."
        )

        full_text = transcription_result["transcription"]

        # 2. Simple heuristic action extraction (kept from before)
        action_items = self._extract_action_heuristics(full_text)

        return {
            "transcription": full_text,
            "segments": [],  # Whisper-Large-v3 json does not give segments by default
            "action_items": action_items,
            "duration": 0,   # not returned by SambaNova
            "metadata": {
                "filename": filename,
                "word_count": len(full_text.split()),
                "language": transcription_result.get("language"),
                "provider": "SambaNova Whisper-Large-v3"
            }
        }

    def _extract_action_heuristics(self, text: str) -> List[Dict[str, Any]]:
        """Same simple heuristics as before."""
        import re
        action_patterns = [
            r"(?:need to|should|must|will|going to)\s+([^.]+)",
            r"(?:action item|todo|task|follow.up|followup)[:\s]+([^.]+)",
            r"(?:@(\w+)).*?(?:need to|should|will)\s+([^.]+)"
        ]

        actions = []
        for pattern in action_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                actions.append({
                    "text": match.group(0),
                    "assignee": match.group(1) if "@" in match.group(0) else None,
                    "confidence": "high" if "action item" in match.group(0).lower() else "medium"
                })
        return actions