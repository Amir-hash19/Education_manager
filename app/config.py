from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str = "test"
    REDIS_URL: str = "redis://localhost:6379/1"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "admin"
    DB_PASSWORD: str = "amir112233"
    DB_NAME: str = "edumanage"
    CELERY_BROKER_URL: str = "redis://redis:6379/3"
    CELERY_BACKEND_URL: str = "redis://redis:6379/3"

     
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None



    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

