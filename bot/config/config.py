from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str
    API_KEY: str

    SLEEP_RANDOM: list = [5, 10]
    SLEEP_BETWEEN_TAP: list[int] = [10, 15]
    SLEEP_BETWEEN_MINING: list[int] = [1800, 3600]

    AUTO_TAP: bool = True
    AUTO_TASK: bool = True
    AUTO_SPIN: bool = True

    #BOOST
    APPLY_DAILY_ENERGY: bool = True
    APPLY_DAILY_TURBO: bool = True

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()