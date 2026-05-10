from dataclasses import dataclass
from datetime import time
from typing import List


@dataclass
class ScheduleRule:
    id: int
    mac: str
    enabled: bool = True
    start_time: time = time(22, 0)
    end_time: time = time(7, 0)
    days: List[int] = None  # 0=Mon, 6=Sun; None = every day

    def __post_init__(self):
        if self.days is None:
            self.days = list(range(7))
