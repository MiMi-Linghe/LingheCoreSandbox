import os
from datetime import datetime
from typing import Optional

STRATEGY_LOG   = "/var/log/linghe/strategy.log"
HEARTBEAT_LOG  = "/var/log/linghe/soul_heartbeat.log"
EVENTS_LOG     = "/var/log/linghe/events.log"

def _write(path: str, line: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "ab") as f:
        f.write(line.encode("utf-8"))

def log_heartbeat(msg: str, extra_path: Optional[str] = None):
    ts   = datetime.now().strftime("[%Y-%m-%d %H:%M:%S %z]")
    line = f"{ts} {msg}\n"
    _write(STRATEGY_LOG, line)
    _write(HEARTBEAT_LOG, line)
    if extra_path:
        _write(extra_path, line)
    print(line.strip())

def log_event(msg: str):
    ts   = datetime.now().strftime("[%Y-%m-%d %H:%M:%S %z]")
    line = f"{ts} {msg}\n"
    _write(EVENTS_LOG, line)
    print(line.strip())
