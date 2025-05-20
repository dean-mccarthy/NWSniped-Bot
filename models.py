from dataclasses import dataclass, asdict

@dataclass
class User:
    snipes: float = 0.0
    times_sniped: float = 0.0
    acheivements: list[str] = None

    @staticmethod
    def from_dict(data):
        return User(**data)

    def to_dict(self):
        return asdict(self)
    
    
@dataclass
class ServerConfig:
    points_per_snipe: float = 1.0
    penalty_per_snipe: float = 1.0
    acheivements_enabled: bool = True

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: dict):
        return ServerConfig(**data)