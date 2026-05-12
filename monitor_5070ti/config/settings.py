from functools import lru_cache
import os


class Settings:
    def __init__(self) -> None:
        self.check_interval_sec = int(os.getenv('CHECK_INTERVAL_SEC', '60'))
        self.request_timeout_sec = int(os.getenv('REQUEST_TIMEOUT_SEC', '10'))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
