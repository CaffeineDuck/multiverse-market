from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DB__HOST: str = "localhost"
    DB__PORT: int = 5432
    DB__USER: str = "postgres"
    DB__PASSWORD: str = "postgres"
    DB__NAME: str = "multiverse_market"
    DB__SSL: bool = False
    
    @property
    def DATABASE_URL(self) -> str:
        ssl = "?ssl=true" if self.DB__SSL else ""
        return f"postgresql+asyncpg://{self.DB__USER}:{self.DB__PASSWORD}@{self.DB__HOST}:{self.DB__PORT}/{self.DB__NAME}{ssl}"
    
    DB_ECHO: bool = True  # Enable for debugging
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS__HOST: str = "localhost"
    REDIS__PORT: int = 6379
    REDIS__DB: int = 0
    REDIS__PASSWORD: str = ""
    REDIS__SSL: bool = False
    
    @property
    def REDIS_URL(self) -> str:
        password = f":{self.REDIS__PASSWORD}@" if self.REDIS__PASSWORD else ""
        ssl = "?ssl=true" if self.REDIS__SSL else ""
        return f"redis://{password}{self.REDIS__HOST}:{self.REDIS__PORT}/{self.REDIS__DB}{ssl}"
    
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Multiverse Market"
    VERSION: str = "0.1.0"
    DEBUG: bool = True  # Enable for debugging
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 