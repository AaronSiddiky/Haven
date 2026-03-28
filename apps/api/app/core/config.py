from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Haven API"
    debug: bool = False

    # Supabase
    supabase_url: str
    supabase_service_key: str

    # LiveKit
    livekit_api_key: str = ""
    livekit_api_secret: str = ""
    livekit_ws_url: str = ""

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # OpenClaw
    openclaw_gateway_url: str = ""
    openclaw_api_key: str = ""

    # App
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
