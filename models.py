from dataclasses import dataclass, asdict, field
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from typing import List, Literal, Tuple
from enum import Enum

PACIFIC = ZoneInfo("Canada/Pacific")

@dataclass
class SafeTime:
    day: int #Monday = 0, Sunday = 6
    start_time: time
    end_time: time

    def to_dict(self):
        return {
            "day": self.day,
            "start_time": self.start_time.isoformat(timespec="minutes"),
            "end_time": self.end_time.isoformat(timespec="minutes")
        }

    @staticmethod
    def from_dict(data: dict):
        return SafeTime(
            day=data["day"],
            start_time=time.fromisoformat(data["start_time"]),
            end_time=time.fromisoformat(data["end_time"])
        )
    
    def check_safe(self, now) -> bool:
        local_time = now.astimezone(PACIFIC)
        buffer = timedelta(minutes=15)

        if local_time.weekday() != self.day:
            return False
        
        start_buf = datetime.combine(local_time.date(), self.start_time) - buffer
        end_buf = datetime.combine(local_time.date(), self.end_time) + buffer
        return start_buf <= local_time.time() <= end_buf

@dataclass
class User:
    user_id: int # discord id NOT USED for _id in Mongo
    guild_id: int
    snipes: int = 0
    times_sniped: int = 0
    kill_streak: int = 0
    achievements: list[str] = None
    targets: list[int] = None

    @staticmethod
    def from_dict(data):
        return User(
            user_id=data["user_id"],
            guild_id=data["guild_id"],
            snipes=data.get("snipes", 0),
            times_sniped=data.get("times_sniped", 0),
            kill_streak=data.get("kill_streak", 0),
            achievements=data.get("achievements", []) or [],
            targets=data.get("targets", []) or []
        )

    def to_dict(self):
        data = asdict(self)
        return data
    
    
@dataclass
class ServerConfig:
    guild_id: int # used as _id for Mongo
    points_per_snipe: float = 1.0
    penalty_per_snipe: float = 1.0
    achievements_enabled: bool = True
    safe_times: List[SafeTime] = None # (day, start_time, end_time)
    paused: bool = False
    channel: int = 0

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
            safe_times=[SafeTime.from_dict(st) for st in data.get("safe_times", [])],
            paused=data.get("paused", False),
            channel=data.get("channel", 0),
        )
    

@dataclass
class Snipe:
    guild_id: int
    sniper_id: int
    target_id: int
    channel: int
    confirmed: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(ZoneInfo("Canada/Pacific")).isoformat())

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Snipe(
            guild_id=data["guild_id"],
            sniper_id=data["sniper_id"],
            target_id=data["target_id"],
            confirmed=data.get("confirmed", False),
            timestamp=data.get("timestamp"),
            channel=data.get("channel"),
        )
    
    def format_timestamp(self) -> str:
        dt = datetime.fromisoformat(self.timestamp).astimezone(ZoneInfo("Canada/Pacific"))
        return dt.strftime("%b %d, %H:%M")
    


@dataclass
class InGameAchvContext:
    guild_id: int
    sniper_data: User
    target_data: User
    s_snipes: list
    t_snipes: list
    

@dataclass(frozen=True)
class AchievementData:
    name: str
    point_value: int


class AchievementName(Enum):
    KILL_STREAK             = AchievementData("Kill Streak", 2)
    SHUT_DOWN               = AchievementData("Shut Down", 1)
    REVENGEFUL              = AchievementData("Revengeful", 1)
    LOVE_TRIANGLE           = AchievementData("Love Triangle", 1)
    SCREEN_PEEK             = AchievementData("Screen Peek", 0.5)
    CAMPER                  = AchievementData("Camper", 0.5)
    NOTHING_PERSONNEL       = AchievementData("Nothing Personnel", 1.0)
    SPONSORED_BY_TRANSLINK  = AchievementData("Sponsored by TransLink", 1.0)
    THOMAS_THE_TANK         = AchievementData("Thomas the Tank", 2.0)
    PIRATE                  = AchievementData("Pirate", 2.0)
    DOPPLEGANGER            = AchievementData("Doppleganger", -0.5)
    HOME_PLATE              = AchievementData("Home Plate", -1.0)
    VIRTUAL_INSANITY        = AchievementData("Virtual Insanity", 0.5)
    ASSIST_TROPHY           = AchievementData("Assist Trophy", 0.5)
    GHOSTS_OF_THE_PAST      = AchievementData("Ghosts of the Past", 0.5)
    PERFECTLY_BALANCED      = AchievementData("Perfectly Balanced", 2.0)
    SITTING_DUCK            = AchievementData("Sitting Duck", 2.0)
    LICENSE_TO_KILL         = AchievementData("License to Kill", 1.0)
    SNEAKY_BEAKY            = AchievementData("Sneaky Beaky", 1.0)
    PACIFIST                = AchievementData("Pacifist", 1.0)
    COMPLETED_POKEDEX       = AchievementData("Completed Pokedex", 3.0)


