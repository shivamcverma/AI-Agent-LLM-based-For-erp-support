from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    openrouter_api_key: str
    erp_chatbot_base_url: str
    erp_chatbot_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()