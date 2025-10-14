from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str = "test"
    REDIS_URL: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str



    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

