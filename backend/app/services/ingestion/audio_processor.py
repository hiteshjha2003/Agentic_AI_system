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

        # 2. Intelligent Analysis with SambaNova (Replaces simple heuristics)
        analysis = await self._analyze_meeting_with_llm(full_text, participants)

        return {
            "transcription": full_text,
            "summary": analysis.get("summary", ""),
            "action_items": analysis.get("action_items", []),
            "metadata": {
                "filename": filename,
                "word_count": len(full_text.split()),
                "language": transcription_result.get("language"),
                "provider": "SambaNova Whisper-Large-v3 + Llama-3"
            }
        }

    async def _analyze_meeting_with_llm(
        self,
        text: str,
        participants: List[str]
    ) -> Dict[str, Any]:
        """Use SambaNova LLM to summarize and extract actions."""
        
        prompt = f"""Analyze this meeting transcript. 
Participants: {', '.join(participants) if participants else 'Unknown'}

Transcript:
{text[:4000]} # Limit to 4k tokens for safety

Provide:
1. A concise 3-sentence summary of the meeting.
2. A list of specific action items, each with an assignee if possible.

Format as JSON:
{{
  "summary": "...",
  "action_items": [
    {{"text": "...", "assignee": "..."}},
    ...
  ]
}}
"""
        try:
            # Use the chat model for structured extraction
            response = await self.sambanova.client.chat.completions.create(
                model=self.sambanova.models["chat"],
                messages=[
                    {"role": "system", "content": "You are a professional meeting assistant. Extract structured data in JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM Audio Analysis failed: {e}")
            # Fallback to heuristics
            return {
                "summary": "Meeting transcript processed. Heuristic extraction used.",
                "action_items": self._extract_action_heuristics(text)
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