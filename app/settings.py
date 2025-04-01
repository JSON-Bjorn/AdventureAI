from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_URL: str
    OPENAI_API_KEY: str
    STABLE_DIFFUSION_PORT: str
    MISTRAL_PORT: str
    MAILGUN_API_KEY: str
    MAILGUN_DOMAIN: str
    MAILGUN_EMAIL: str


settings = Settings()
