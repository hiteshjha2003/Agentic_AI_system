# backend/app/services/analysis/action_generator.py
from typing import List, Dict, Any, Optional
from app.services.sambanova_client import SambaNovaOrchestrator
from app.models.schemas import SuggestedAction

class ActionGenerator:
    """
    Generates executable actions based on analysis.
    Uses function calling to structure outputs.
    """

    def __init__(self):
        self.sambanova = SambaNovaOrchestrator()

    async def generate_actions(
        self,
        query: str,
        contexts: List[Dict[str, Any]],
        analysis_type: str,
        custom_tools: Optional[List[Dict[str, Any]]] = None
    ) -> List[SuggestedAction]:
        """
        Generate actions using provided or default tools.
        """
        tools = custom_tools or self._get_default_tools()

        raw_actions = await self.sambanova.generate_actions(
            query=query,
            relevant_code=contexts,
            analysis_type=analysis_type,
            available_tools=tools
        )

        # Map to SuggestedAction
        actions = []
        for raw in raw_actions:
            args = raw["arguments"]
            action_type = raw["action_type"]

            if action_type == "edit_file":
                actions.append(SuggestedAction(
                    action_type="edit",
                    target_file=args.get("file_path"),
                    description=args.get("explanation"),
                    diff=args.get("replacement"),
                    reasoning=raw["reasoning"],
                    confidence=0.85  # Placeholder
                ))
            elif action_type == "create_test":
                actions.append(SuggestedAction(
                    action_type="test",
                    target_file=args.get("test_file"),
                    description=args.get("description"),
                    new_content=args.get("test_code"),
                    reasoning=raw["reasoning"],
                    confidence=0.85
                ))
            # Add more mappings as needed

        return actions

    def _get_default_tools(self) -> List[Dict[str, Any]]:
        """Default set of tools for action generation."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Propose a code edit",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "line_start": {"type": "integer"},
                            "line_end": {"type": "integer"},
                            "replacement": {"type": "string"},
                            "explanation": {"type": "string"}
                        },
                        "required": ["file_path", "replacement", "explanation"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_test",
                    "description": "Generate a test case",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "test_file": {"type": "string"},
                            "test_code": {"type": "string"},
                            "description": {"type": "string"}
                        },
                        "required": ["test_file", "test_code", "description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Recommend deleting a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["file_path", "reason"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pr_comment",
                    "description": "Add a comment to a PR",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pr_id": {"type": "string"},
                            "comment": {"type": "string"},
                            "position": {"type": "object", "properties": {"file": {"type": "string"}, "line": {"type": "integer"}}}
                        },
                        "required": ["pr_id", "comment"]
                    }
                }
            }
        ]