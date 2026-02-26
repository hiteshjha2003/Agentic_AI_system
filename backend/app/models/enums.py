# backend/app/models/enums.py
from enum import Enum, auto

class IngestionType(Enum):
    SCREENSHOT = auto()
    AUDIO = auto()
    CODE_SNIPPET = auto()
    ERROR_LOG = auto()
    PR_DESCRIPTION = auto()

class AnalysisType(Enum):
    DEBUG = auto()
    REVIEW = auto()
    REFACTOR = auto()
    EXPLAIN = auto()
    TEST_GENERATE = auto()

class ActionType(Enum):
    EDIT = auto()
    CREATE = auto()
    DELETE = auto()
    TEST = auto()
    PR_COMMENT = auto()
    SLACK_NOTIFY = auto()