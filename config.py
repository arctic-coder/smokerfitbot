from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    bot_token: str
    host: str
    port: int
    log_level: str
    autobill_interval_sec: int
    client_max_size: int  # bytes

    @staticmethod
    def from_env() -> "Config":
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise RuntimeError("BOT_TOKEN is not set")
        return Config(
            bot_token=token,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8080")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            autobill_interval_sec=int(os.getenv("AUTOBILL_INTERVAL_SEC", "600")),
            client_max_size=int(os.getenv("CLIENT_MAX_SIZE", str(256*1024))),
        )
