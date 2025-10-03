from dotenv import load_dotenv
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class TelegramBotConfig(BaseSettings):
    token: SecretStr = Field(description="Telegram bot token")
    debug: bool = Field(description="ORM logs, Swagger show", default=False)

    model_config = SettingsConfigDict(env_prefix="TELEGRAM_BOT_", env_file_encoding="utf-8")


class PostgresConfig(BaseSettings):
    user: str = Field(
        default="postgres",
    )
    password: SecretStr = Field(description="<PASSWORD>")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=5432)
    db: str = Field(default="telegram_bot_db")

    @property
    def dsn(self):
        return (
            f"postgresql+asyncpg://{self.user}:"
            + f"{self.password.get_secret_value()}@{self.host}:"
            + f"{self.port}/{self.db}"
        )

    model_config = SettingsConfigDict(env_prefix="POSTGRES_", env_file_encoding="utf-8")


class Config(BaseSettings):
    telegram_bot: TelegramBotConfig = TelegramBotConfig()
    postgres: PostgresConfig = PostgresConfig()


config = Config()
