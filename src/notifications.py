import requests

from src.config import Config
from src.logger import Logger


def send_discord_notification(message: str, is_error: bool = False):
    if not Config.DISCORD_WEBHOOK_URL:
        return
    prefix = "❌" if is_error else "✅"
    try:
        requests.post(Config.DISCORD_WEBHOOK_URL, json={"content": f"{prefix} {message}"}, timeout=10)
    except Exception as e:
        Logger.warning(f"Discord notification failed: {e}")
