# backend/app/services/ingestion/vision_processor.py
import base64
import json
import asyncio
from typing import Dict, Any, Optional
from app.services.sambanova_client import SambaNovaOrchestrator

class VisionProcessor:
    """
    Pure SambaNova Vision processor – zero local image processing.
    Sends raw bytes as base64 to SambaNova multimodal model.
    Forces structured JSON output.
    """

    def __init__(self):
        self.sambanova = SambaNovaOrchestrator()

    async def process_screenshot(
        self,
        image_bytes: bytes,
        source: str = "unknown",
        nearby_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send raw image bytes to SambaNova Vision model.
        Always returns 'combined_extracted_text' as string.
        """
        bytes_size = len(image_bytes)
        if bytes_size < 100:
            return {
                "status": "failed",
                "error": "Empty or too small image (<100 bytes)",
                "bytes_size": bytes_size,
                "source": source,
                "combined_extracted_text": ""
            }

        try:
            # Base64 encode raw bytes
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            mime = "image/png"  # Safe default
            image_url = f"data:{mime};base64,{base64_image}"

            # Structured JSON prompt
            prompt = f"""
Analyze this screenshot from {source} in detail. 
If it is a flowchart, architectural diagram, or UI design, provide a deep technical breakdown.

Context: {nearby_code or 'none'}.

Return **ONLY valid JSON** (no markdown, no extra text) with these exact keys:
{{
  "extracted_text": "All visible text from the image, line by line",
  "detailed_explanation": "Provide a comprehensive technical explanation of the image content, specifically explaining logic, connections, and architecture if visible.",
  "layout_description": "Describe visual layout, UI elements, colors, structure",
  "architectural_components": ["Component 1", "Component 2"],
  "issue_type": "bug / performance / UI / syntax / crash / other / none",
  "severity": "low / medium / high / critical / none",
  "hypotheses": ["Possible technical cause 1", "Possible technical cause 2"]
}}
"""

            # Call SambaNova with timeout & retry
            vision_response = None
            for attempt in range(1, 4):
                try:
                    vision_response = await asyncio.wait_for(
                        self.sambanova.client.chat.completions.create(
                            model="Llama-4-Maverick-17B-128E-Instruct",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {"type": "image_url", "image_url": {"url": image_url}}
                                    ]
                                }
                            ],
                            max_tokens=2048,
                            temperature=0.1
                        ),
                        timeout=120
                    )
                    break
                except asyncio.TimeoutError:
                    if attempt == 3:
                        raise TimeoutError("SambaNova Vision timed out after 3 attempts")
                    await asyncio.sleep(2)

            if not vision_response:
                raise ValueError("No response from SambaNova")

            analysis_text = vision_response.choices[0].message.content.strip()

            # Parse JSON
            try:
                parsed = json.loads(analysis_text)
            except json.JSONDecodeError:
                parsed = {"raw_response": analysis_text}

            # Build result – ALWAYS string for extracted_text
            result = {
                "status": "success",
                "source": source,
                "vision_analysis": parsed,
                "combined_extracted_text": str(parsed.get("extracted_text", "")),
                "detailed_explanation": parsed.get("detailed_explanation", ""),
                "architectural_components": parsed.get("architectural_components", []),
                "issue_classification": {
                    "type": parsed.get("issue_type", "none"),
                    "severity": parsed.get("severity", "none")
                },
                "hypotheses": parsed.get("hypotheses", []),
                "bytes_size": bytes_size
            }

            return result

        except Exception as e:
            error_msg = str(e) if str(e) else "Unknown error"
            return {
                "status": "failed",
                "error": f"SambaNova Vision failed: {error_msg}",
                "bytes_size": bytes_size,
                "source": source,
                "combined_extracted_text": "",  # empty string on failure
                "hint": "Check API key, model name, network, or try smaller image"
            }