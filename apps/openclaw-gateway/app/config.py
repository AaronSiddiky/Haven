from functools import lru_cache

from pydantic_settings import BaseSettings


class GatewaySettings(BaseSettings):
    haven_api_url: str = "http://localhost:8000"
    haven_api_key: str = ""
    gateway_port: int = 9090
    gateway_label: str = "local-dev"
    machine_name: str = "macbook"
    headless: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> GatewaySettings:
    return GatewaySettings()
