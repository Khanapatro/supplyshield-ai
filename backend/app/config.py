from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # FalkorDB Connection Settings
    FALKORDB_HOST: str = "127.0.0.1"
    FALKORDB_PORT: int = 6379
    FALKORDB_GRAPH_NAME: str = "supplyshield"

    # API Settings
    APP_NAME: str = "SupplyShield AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Data Settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_FILE: Path = BASE_DIR / "data" / "synthetic_supply_chain.json"


settings = Settings()
