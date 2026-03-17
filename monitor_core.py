import hashlib
import json
import logging
import os
import re
import smtplib
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from typing import Callable, Dict, List, Optional

import requests


LOG_FILE = "tcf_monitor.log"
CONFIG_FILE = "tcf_monitor_config.json"
ENV_FILE = "config.env"
TARGETS_FILE = "targets.json"

logger = logging.getLogger("tcf_monitor")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)


def load_targets() -> List[dict]:
    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def send_email(subject: str, body: str, email: str, password: str, to_email: str) -> None:
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = to_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20)
    server.login(email, password)
    server.sendmail(email, [to_email], msg.as_string())
    server.quit()


# 🔥 新增：检测是否有真实日期
def has_real_date(text: str) -> bool:
    patterns = [
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b",
        r"\b\d{1,2}\s?(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b",
        r"\b\d{4}\b"
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


@dataclass
class CheckResult:
    location: str
    available: bool
    changed: bool
    detail: str


class MonitorEngine:
    def __init__(self, ui_callback: Optional[Callable[[str], None]] = None):
        self.ui_callback = ui_callback
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None
        self.state: Dict[str, Dict[str, bool]] = {}

    def log(self, message: str) -> None:
        logger.info(message)
        if self.ui_callback:
            self.ui_callback(message)

    def fetch(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.text

    def evaluate_target(self, target: dict) -> CheckResult:
        html = self.fetch(target["url"])
        name = target["name"]

        blocked = target.get("keywords", [])

        no_sold_out = all(word.lower() not in html.lower() for word in blocked)
        has_date = has_real_date(html)

        # 🔥 核心：只有“有日期”才算可用
        available = no_sold_out and has_date

        detail = "Date-based availability check"

        return CheckResult(
            location=name,
            available=available,
            changed=False,
            detail=detail
        )

    def run_once(self, email: str, password: str, to_email: str, enabled_names: List[str]) -> None:
        targets = [t for t in load_targets() if t.get("enabled", True) and t["name"] in enabled_names]

        for t in targets:
            try:
                result = self.evaluate_target(t)

                self.log(f"Checked {result.location} | available={result.available}")

                previous = self.state.get(result.location, {})
                last_available = previous.get("last_available", False)

                # ✅ 只在 False → True 才提醒
                if result.available and not last_available:
                    subject = f"TCF Seat Alert - {result.location}"
                    body = (
                        f"检测到 {result.location} 出现新的考试日期！\n\n"
                        f"Location: {result.location}\n"
                        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"请尽快打开网站抢位：\n{t['url']}\n"
                    )
                    send_email(subject, body, email, password, to_email)
                    self.log(f"Alert email sent for {result.location}")

                self.state[result.location] = {
                    "last_available": result.available
                }

            except Exception as e:
                self.log(f"Error checking {t['name']}: {e}")

    def start(self, email: str, password: str, to_email: str, interval: int, enabled_names: List[str]) -> None:
        if self.thread and self.thread.is_alive():
            self.log("Monitor already running.")
            return

        self.stop_event.clear()

        def worker():
            self.log("Monitor started.")
            while not self.stop_event.is_set():
                self.run_once(email, password, to_email, enabled_names)
                for _ in range(interval):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
            self.log("Monitor stopped.")

        self.thread = threading.Thread(target=worker, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()