from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Device:
    ip: str
    mac: str
    hostname: str = "Unknown"
    vendor: str = "Unknown"
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    online: bool = False
    blocked: bool = False
    signal_strength: Optional[int] = None

    @property
    def mac_vendor_key(self) -> str:
        return self.mac[:8].upper() if self.mac else ""
