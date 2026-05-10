import threading
import time
from datetime import datetime, time as dtime
from typing import List, Callable, Optional

from ..models.rule import ScheduleRule
from ..utils.storage import load_rules, save_rules


class Scheduler:
    def __init__(self, block_callback: Callable[[str, str], None],
                 unblock_callback: Callable[[str], None],
                 is_blocked_fn: Callable[[str], bool]):
        self._rules: List[ScheduleRule] = []
        self._block_cb = block_callback
        self._unblock_cb = unblock_callback
        self._is_blocked_fn = is_blocked_fn
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def load(self):
        self._rules = load_rules()

    def save(self):
        save_rules(self._rules)

    @property
    def rules(self) -> List[ScheduleRule]:
        return self._rules

    def add_rule(self, rule: ScheduleRule):
        self._rules.append(rule)
        self.save()

    def remove_rule(self, rule_id: int):
        self._rules = [r for r in self._rules if r.id != rule_id]
        self.save()

    def update_rule(self, rule: ScheduleRule):
        for i, r in enumerate(self._rules):
            if r.id == rule.id:
                self._rules[i] = rule
                break
        self.save()

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        while self._running:
            now = datetime.now()
            current_day = now.weekday()
            current_minutes = now.hour * 60 + now.minute

            for rule in self._rules:
                if not rule.enabled:
                    continue
                if rule.days and current_day not in rule.days:
                    continue

                start_m = rule.start_time.hour * 60 + rule.start_time.minute
                end_m = rule.end_time.hour * 60 + rule.end_time.minute

                should_block: bool
                if start_m < end_m:
                    should_block = start_m <= current_minutes < end_m
                else:
                    should_block = current_minutes >= start_m or current_minutes < end_m

                mac = rule.mac
                currently_blocked = self._is_blocked_fn(mac)

                if should_block and not currently_blocked:
                    self._block_cb(mac, "0.0.0.0")
                elif not should_block and currently_blocked:
                    self._unblock_cb(mac)

            time.sleep(30)
