from pydantic import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_URL: str
    OPENAI_API_KEY: str
    STABLE_DIFFUSION_PORT: str
    MISTRAL_PORT: str


settings = Settings()
