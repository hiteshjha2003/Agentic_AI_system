# backend/app/services/history_manager.py
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class HistoryManager:
    def __init__(self, storage_path: str = "backend/data/history.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump([], f)

    def save_entry(self, entry_type: str, data: Dict[str, Any], query: Optional[str] = None):
        """Save a new history entry."""
        history = self.get_all()
        
        new_entry = {
            "id": data.get("id") or data.get("request_id") or str(len(history) + 1),
            "type": entry_type,
            "timestamp": datetime.utcnow().isoformat(),
            "query": query or data.get("query") or "N/A",
            "data": data
        }
        
        history.insert(0, new_entry) # Most recent first
        
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        with open(self.storage_path, "w") as f:
            json.dump(history, f, indent=2, default=json_serial)
        
        return new_entry

    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieve all history entries."""
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def clear(self):
        """Clear all history."""
        with open(self.storage_path, "w") as f:
            json.dump([], f)
