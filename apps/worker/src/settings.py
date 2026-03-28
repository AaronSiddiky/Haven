from functools import lru_cache

from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):
    supabase_url: str
    supabase_service_key: str

    openai_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # NWS polling
    nws_poll_states: str = "CA,TX,FL,NY"
    poll_interval_seconds: int = 300

    # Alert expiry
    expiry_check_interval_seconds: int = 600

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def states_list(self) -> list[str]:
        return [s.strip() for s in self.nws_poll_states.split(",") if s.strip()]


@lru_cache()
def get_settings() -> WorkerSettings:
    return WorkerSettings()
