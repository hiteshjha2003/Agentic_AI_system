# backend/app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import uuid
from enum import Enum


class IngestionType(str, Enum):
    SCREENSHOT = "screenshot"
    AUDIO = "audio"
    CODE_SNIPPET = "code_snippet"
    ERROR_LOG = "error_log"
    PR_DESCRIPTION = "pr_description"

class AnalysisType(str, Enum):
    DEBUG = "debug"
    REVIEW = "review"
    REFACTOR = "refactor"
    EXPLAIN = "explain"
    TEST_GENERATE = "test_generate"

class CodeLocation(BaseModel):
    file_path: str
    line_start: int
    line_end: int
    git_commit: Optional[str] = None

class IngestedContext(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: IngestionType
    source: str                     # file path, meeting name, etc.
    content: str                    # extracted text/code
    raw_data: Optional[bytes] = None
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    embedding_id: Optional[str] = None

class AnalysisRequest(BaseModel):
    query: str
    context_ids: List[str] = []     # Specific contexts to include
    analysis_type: AnalysisType
    code_location: Optional[CodeLocation] = None
    include_codebase: bool = True
    stream: bool = False

class SuggestedAction(BaseModel):
    action_type: Literal[
        "edit", "create", "delete", "test", "pr_comment", "slack_notify",
        "edit_file", "create_test", "create_pr_comment"   # ← add raw tool names
    ]
    target_file: str
    description: str
    diff: Optional[str] = None      # Unified diff format
    new_content: Optional[str] = None
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)

class AnalysisResponse(BaseModel):
    request_id: str
    summary: str
    detailed_analysis: str
    relevant_contexts: List[IngestedContext]
    suggested_actions: List[SuggestedAction]
    follow_up_questions: List[str]
    execution_time_ms: int