from datetime import datetime


class Logger:
    @staticmethod
    def _ts():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def info(msg):
        print(f"[{Logger._ts()}] [INFO] {msg}")

    @staticmethod
    def success(msg):
        print(f"[{Logger._ts()}] [SUCCESS] ✅ {msg}")

    @staticmethod
    def warning(msg):
        print(f"[{Logger._ts()}] [WARNING] ⚠️ {msg}")

    @staticmethod
    def error(msg):
        print(f"[{Logger._ts()}] [ERROR] ❌ {msg}")
