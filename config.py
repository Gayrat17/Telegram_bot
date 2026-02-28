from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str = Field()
    POSTGRES_PASSWORD: str = Field()
    POSTGRES_HOST: str = Field()
    POSTGRES_PORT: int = Field()
    POSTGRES_DATABASE: str = Field()

    @property
    def postgresql_url(self) -> str:
        return (f"postgresql://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")

    @property
    def async_postgresql_url(self) -> str:
        return (f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
                f"{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}")

    class Config:
        env_file = '.env'


settings = Settings()
