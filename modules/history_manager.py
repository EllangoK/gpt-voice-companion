import json
from collections import namedtuple
from typing import List, Tuple
import datetime

HistoryEntry = namedtuple("HistoryEntry", ["message", "audio_path"])

class HistoryManager:
    def __init__(self):
        self.history: List[Tuple[HistoryEntry, HistoryEntry]] = []
        self.timestamp = datetime.datetime.now()

    def add_entry(self, user_entry: HistoryEntry, ai_entry: HistoryEntry):
        entry_pair = (user_entry, ai_entry)
        self.history.append(entry_pair)

    def get_history(self) -> List[Tuple[HistoryEntry, HistoryEntry]]:
        return self.history

    def clear_history(self):
        self.history = []

    def to_json(self) -> str:
        serialized_history = [
            {
                "user": {"message": user_entry.message, "audio_path": user_entry.audio_path},
                "ai": {"message": ai_entry.message, "audio_path": ai_entry.audio_path},
            }
            for user_entry, ai_entry in self.history
        ]
        serialized_history = {"history": serialized_history, "timestamp": self.timestamp.isoformat()}
        return json.dumps(serialized_history, indent=2)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        hm = cls()
        hm.timestamp = datetime.datetime.fromisoformat(data["timestamp"])
        hm.history = [
            (HistoryEntry(**entry["user"]), HistoryEntry(**entry["ai"]))
            for entry in data["history"]
        ]
        return hm

    def __str__(self) -> str:
        history_str = []
        for user_entry, ai_entry in self.history:
            history_str.extend([user_entry.message, ai_entry.message])
        return "\n".join(history_str)

    def to_str(self) -> str:
        return str(self)
    
    def clear(self):
        self.history = []

    def __getitem__(self, index: int) -> Tuple[HistoryEntry, HistoryEntry]:
        return self.history[index]

    def __setitem__(self, index: int, value: Tuple[HistoryEntry, HistoryEntry]):
        self.history[index] = value

    def add_audio_path_to_last_entry(self, audio_path: str, is_user: bool):
        if is_user:
            user_entry = self.history[-1][0]._replace(audio_path=audio_path)
            ai_entry = self.history[-1][1]
        else:
            user_entry = self.history[-1][0]
            ai_entry = self.history[-1][1]._replace(audio_path=audio_path)
        self.history[-1] = (user_entry, ai_entry)
