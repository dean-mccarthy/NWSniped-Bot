from dataclasses import dataclass, asdict
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Tuple

@dataclass
class SafeTime:
    day: str
    start_time: str
    end_time: str

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        return SafeTime(
            day=data["day"],
            start_time=data["start_time"],
            end_time=data["end_time"]
        )

@dataclass
class User:
    user_id: int # discord id used for _id in Mongo
    guild_id: int
    snipes: int = 0
    times_sniped: int = 0
    achievements: list[str] = None

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data["_id"],
            guild_id=data["guild_id"],
            snipes=data.get("snipes", 0),
            times_sniped=data.get("times_sniped", 0),
            achievements=data.get("achievements", []) or []
        )

    def to_dict(self):
        data = asdict(self)
        data["_id"] = data.pop("user_id")
        return data
    
    
@dataclass
class ServerConfig:
    guild_id: int # used as _id for Mongo
    points_per_snipe: float = 1.0
    penalty_per_snipe: float = 1.0
    achievements_enabled: bool = True
    safe_times: List[SafeTime] = None # (day, start_time, end_time)

    def to_dict(self):
        data = asdict(self)
        data["_id"] = data.pop("guild_id")
        data["safe_times"] = [st.to_dict() for st in self.safe_times] if self.safe_times else []
        return data
    
    @staticmethod
    def from_dict(data: dict):
        return ServerConfig(
            guild_id=data["_id"],
            points_per_snipe=data.get("points_per_snipe", 1.0),
            penalty_per_snipe=data.get("penalty_per_snipe", 1.0),
            achievements_enabled=data.get("achievements_enabled", True),
            safe_times=[SafeTime.from_dict(st) for st in data.get("safe_times", [])]
        )
    

@dataclass
class Snipe:
    guild_id: int
    sniper_id: int
    target_id: int
    timestamp: str = datetime.now(ZoneInfo("Canada/Pacific")).isoformat()

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Snipe(
            guild_id=data["guild_id"],
            sniper_id=data["sniper_id"],
            target_id=data["target_id"],
            timestamp=data.get("timestamp", datetime.utcnow().isoformat())
        )
    
