# backend/app/services/sambanova_client.py
import openai
import json
import base64
from typing import List, Dict, Any, Optional, AsyncGenerator, Callable
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
from app.config import get_settings


class SambaNovaOrchestrator:
    """
    Unified client for SambaNova Cloud multimodal capabilities.
    Handles: Chat, Vision, Embeddings, Function Calling with optimized routing.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.AsyncOpenAI(
            api_key=self.settings.SAMBANOVA_API_KEY,
            base_url=self.settings.SAMBANOVA_BASE_URL,
            http_client=httpx.AsyncClient(
                limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
                timeout=httpx.Timeout(60.0, connect=10.0)
            )
        )
        
        # Model routing based on task
        self.models = {
            "vision": self.settings.SAMBANOVA_MODEL_VISION,
            "chat": self.settings.SAMBANOVA_MODEL_CHAT,
            "embedding": self.settings.SAMBANOVA_MODEL_EMBEDDING,
        }
    
    # ═══════════════════════════════════════════════════════════════
    # VISION + CODE ANALYSIS
    # ═══════════════════════════════════════════════════════════════
    
    async def analyze_screenshot(
        self, 
        image_bytes: bytes, 
        context: str = "",
        code_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze screenshot of code/error with vision model.
        """
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert code debugger analyzing screenshots.
Extract all visible code, error messages, and UI elements.
Identify the programming language, framework, and likely issue."""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Analyze this screenshot. Context: {context}
{f"Nearby code: {code_hint}" if code_hint else ""}

Provide:
1. Extracted code/error text (verbatim)
2. Programming language & framework detected
3. Type of issue (syntax, runtime, logic, UI)
4. Severity assessment
5. Initial hypotheses (2-3 possibilities)"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model=self.models["vision"],
            messages=messages,
            max_tokens=2048,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        
        # Parse structured output
        return {
            "raw_analysis": content,
            "extracted_text": self._extract_section(content, "Extracted code/error text"),
            "language": self._extract_section(content, "Programming language"),
            "issue_type": self._extract_section(content, "Type of issue"),
            "severity": self._extract_section(content, "Severity"),
            "hypotheses": self._extract_list(content, "Initial hypotheses")
        }
    
    # ═══════════════════════════════════════════════════════════════
    # EMBEDDINGS + CODEBASE SEARCH
    # ═══════════════════════════════════════════════════════════════
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def create_embedding(self, text: str) -> List[float]:
        """Generate embedding for code/text search."""
        response = await self.client.embeddings.create(
            model=self.models["embedding"],
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    
    async def create_code_embedding(self, code: str, context: str = "") -> List[float]:
        """
        Specialized embedding for code with context prefix.
        E5-Mistral performs better with instruction prefix.
        """
        instruction = "Given a code query, retrieve relevant code snippets: "
        formatted = f"{instruction}\nContext: {context}\nCode:\n{code}"
        return await self.create_embedding(formatted)
    
    # ═══════════════════════════════════════════════════════════════
    # FUNCTION CALLING + ACTION GENERATION
    # ═══════════════════════════════════════════════════════════════
    
    async def generate_actions(
        self,
        query: str,
        relevant_code: List[Dict[str, Any]],
        analysis_type: str,
        available_tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate executable actions using function calling.
        """
        
        system_prompt = f"""You are a senior software engineer performing {analysis_type}.
Analyze the provided code context and generate specific, actionable fixes.

Available tools represent actions you can take. Choose appropriately:
- edit_file: Modify existing code
- create_file: Generate new files (tests, implementations)
- run_test: Execute test commands
- create_pr_comment: Add review comment
- search_codebase: If you need more context"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": self._format_context(relevant_code, query)}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.models["chat"],
            messages=messages,
            tools=available_tools,
            tool_choice="auto",
            max_tokens=self.settings.MAX_TOKENS,
            temperature=self.settings.TEMPERATURE
        )
        
        message = response.choices[0].message
        
        actions = []
        if message.tool_calls:
            for tool_call in message.tool_calls:
                actions.append({
                    "action_type": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments),
                    "reasoning": message.content or "No additional reasoning provided"
                })
        
        return actions
    
    # ═══════════════════════════════════════════════════════════════
    # STREAMING ANALYSIS (Real-time)
    # ═══════════════════════════════════════════════════════════════
    
    async def stream_analysis(
        self,
        query: str,
        context: List[Dict[str, Any]],
        analysis_type: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream analysis tokens for real-time UX in VS Code.
        Yields: thought process → code suggestions → final summary
        """
        
        system_prompt = f"""You are analyzing code for {analysis_type}.
Think step by step, then provide your final recommendation.
Use markdown code blocks for any code."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": self._format_context(context, query)}
        ]
        
        stream = await self.client.chat.completions.create(
            model=self.models["chat"],
            messages=messages,
            stream=True,
            max_tokens=self.settings.MAX_TOKENS,
            temperature=0.2
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
        # ──────────────────────────────────────────────────────────────
    # AUDIO TRANSCRIPTION (Whisper-Large-v3)
    # ──────────────────────────────────────────────────────────────
    async def transcribe_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.mp3",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio using SambaNova's Whisper-Large-v3.
        Returns transcription + detected language.
        """
        # Wrap bytes in file-like object (required by OpenAI client)
        from io import BytesIO
        audio_file = BytesIO(audio_bytes)
        audio_file.name = filename

        response = await self.client.audio.transcriptions.create(
            model="Whisper-Large-v3",
            file=audio_file,
            language=language,           # e.g. "en"
            prompt=prompt or "",
            response_format="json",      # or "verbose_json" for timestamps
        )

        return {
            "transcription": response.text,
            "language": getattr(response, "language", None),
            "raw_response": response.model_dump() if hasattr(response, "model_dump") else dict(response),
        }
    
    # ═══════════════════════════════════════════════════════════════
    # ADVANCED: Multi-step Agent Loop
    # ═══════════════════════════════════════════════════════════════
    
    async def agent_loop(
        self,
        initial_query: str,
        context_retriever: Callable[[str], List[Dict[str, Any]]],
        action_executor: Callable[[Dict], Dict[str, Any]],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Autonomous agent that can:
        1. Analyze problem
        2. Retrieve context
        3. Propose actions
        4. Execute and verify
        5. Iterate if needed
        """
        
        conversation = [
            {"role": "system", "content": """You are an autonomous coding agent.
You can search the codebase, propose edits, and verify fixes.
Always explain your reasoning before taking action."""},
            {"role": "user", "content": initial_query}
        ]
        
        actions_taken = []
        
        for iteration in range(max_iterations):
            # Get AI response with potential function calls
            response = await self.client.chat.completions.create(
                model=self.models["chat"],
                messages=conversation,
                tools=self._get_agent_tools(),
                max_tokens=self.settings.MAX_TOKENS
            )
            
            message = response.choices[0].message
            
            # If no tool calls, we're done
            if not message.tool_calls:
                return {
                    "final_answer": message.content,
                    "actions_taken": actions_taken,
                    "iterations": iteration + 1
                }
            
            # Execute tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                # Add to history
                conversation.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [tool_call]
                })
                
                # Execute
                if tool_name == "search_codebase":
                    results = context_retriever(arguments["query"])
                    observation = f"Found {len(results)} relevant files: " + \
                                 ", ".join([r["file_path"] for r in results[:3]])
                    
                elif tool_name == "edit_file":
                    result = await action_executor({
                        "type": "edit",
                        "file": arguments["file_path"],
                        "content": arguments["content"]
                    })
                    observation = f"Edit result: {result['status']}"
                    actions_taken.append(arguments)
                    
                elif tool_name == "run_tests":
                    result = await action_executor({
                        "type": "test",
                        "command": arguments["command"]
                    })
                    observation = f"Test output: {result['output'][:500]}"
                
                else:
                    observation = f"Unknown tool: {tool_name}"
                
                # Add observation to conversation
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": observation
                })
        
        return {
            "final_answer": "Max iterations reached. Current status: " + message.content,
            "actions_taken": actions_taken,
            "iterations": max_iterations
        }
    
    # ═══════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════
    
    def _format_context(self, contexts: List[Dict], query: str) -> str:
        """Format retrieved contexts for the model."""
        formatted = f"Query: {query}\n\nRelevant Code Context:\n"
        for i, ctx in enumerate(contexts[:5], 1):  # Top 5
            formatted += f"\n--- Context {i} ---\n"
            formatted += f"File: {ctx.get('file_path', 'unknown')}\n"
            formatted += f"Type: {ctx.get('type', 'code')}\n"
            formatted += f"Content:\n{ctx.get('content', '')[:2000]}\n"
        return formatted
    
    def _extract_section(self, text: str, header: str) -> str:
        """Extract section from structured analysis output."""
        import re
        pattern = f"{header}[:\s]+([^\n]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_list(self, text: str, header: str) -> List[str]:
        """Extract numbered/bulleted list from text."""
        import re
        pattern = f"{header}.*?(?:\n\s*[-\d]\.?\s*([^\n]+))+" 
        matches = re.findall(r"[-\d]\.?\s*([^\n]+)", text.split(header)[-1].split("\n\n")[0])
        return [m.strip() for m in matches if m.strip()]
    
    def _get_agent_tools(self) -> List[Dict[str, Any]]:
        """Define available tools for agent loop."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_codebase",
                    "description": "Search for relevant code snippets",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Semantic search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_file",
                    "description": "Propose an edit to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "content": {"type": "string", "description": "Full new file content"},
                            "reasoning": {"type": "string"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_tests",
                    "description": "Execute test command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "default": "pytest"},
                            "cwd": {"type": "string"}
                        },
                        "required": ["command"]
                    }
                }
            }
        ]