"""One JSONL log file per run: every line is one step of that run."""

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


class RunLog:
    def __init__(self, directory: Path, model):
        directory.mkdir(parents=True, exist_ok=True)
        self.run_id = uuid.uuid4().hex[:12]
        self.model = model
        self.last_step = time.monotonic()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.path = directory / f"{stamp}_{self.run_id}.jsonl"

    def write(self, event, ok, tool=None, args=None, **details):
        """Log a finished step. Its duration is the time since the previous step ended."""
        now = time.monotonic()
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "event": event,
            "tool": tool,
            "args": args,
            "ok": ok,
            "model": self.model,
            "duration_ms": round((now - self.last_step) * 1000),
            **details,
        }
        self.last_step = now
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
