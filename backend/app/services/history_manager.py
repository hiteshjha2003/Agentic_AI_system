# backend/app/services/history_manager.py
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class HistoryManager:
    def __init__(self, database_dir: Optional[str] = None):
        if database_dir is None:
            # Point to 'database' folder in the project root
            # This assumes the file is at backend/app/services/history_manager.py
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.database_dir = os.path.abspath(os.path.join(base_dir, "../../../database"))
        else:
            self.database_dir = database_dir
        self._ensure_storage()

    def _ensure_storage(self):
        os.makedirs(self.database_dir, exist_ok=True)

    def save_entry(self, entry_type: str, data: Dict[str, Any], query: Optional[str] = None):
        """Save a new history entry into a daily JSON file."""
        now = datetime.utcnow()
        date_str = now.strftime('%Y-%m-%d')
        timestamp = now.isoformat()
        
        import os
        entry_id = data.get("id") or data.get("request_id") or f"{now.strftime('%H%M%S')}_{os.urandom(4).hex()}"
        
        new_entry = {
            "id": entry_id,
            "type": entry_type,
            "timestamp": timestamp,
            "query": query or data.get("query") or "N/A",
            "data": data
        }
        
        file_path = os.path.join(self.database_dir, f"{date_str}.json")
        
        # Load existing entries for the day
        day_entries = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    day_entries = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                day_entries = []
        
        day_entries.insert(0, new_entry)
        
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        with open(file_path, "w") as f:
            json.dump(day_entries, f, indent=2, default=json_serial)
        
        return new_entry

    def get_all(self) -> List[Dict[str, Any]]:
        """Retrieve all history entries by combining all daily JSON files."""
        all_entries = []
        if not os.path.exists(self.database_dir):
            return []
            
        for filename in sorted(os.listdir(self.database_dir), reverse=True):
            if filename.endswith(".json"):
                # Match YYYY-MM-DD.json format
                if len(filename) == 15: # 10 (date) + 5 (.json)
                    file_path = os.path.join(self.database_dir, filename)
                    try:
                        with open(file_path, "r") as f:
                            entries = json.load(f)
                            if isinstance(entries, list):
                                all_entries.extend(entries)
                    except (json.JSONDecodeError, FileNotFoundError):
                        continue
        
        # Final sort by timestamp descending to ensure perfect ordering across days
        all_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return all_entries

    def clear(self):
        """Clear all daily history files."""
        if os.path.exists(self.database_dir):
            for filename in os.listdir(self.database_dir):
                if filename.endswith(".json"):
                    os.remove(os.path.join(self.database_dir, filename))
