"""Configuration management with encryption support."""
import os
from typing import Optional
from pathlib import Path
from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Discord Configuration
    discord_token: str = Field(default="", env="DISCORD_TOKEN")
    discord_guild_id: int = Field(default=0, env="DISCORD_GUILD_ID")
    discord_payment_role_id: int = Field(default=0, env="DISCORD_PAYMENT_ROLE_ID")
    discord_mod_role_id: int = Field(default=0, env="DISCORD_MOD_ROLE_ID")
    
    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///data/gpskilled.db", env="DATABASE_URL")
    
    # FastAPI
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_secret_key: str = Field(default="", env="API_SECRET_KEY")
    
    # Cryptocurrency
    btc_wallet_address: str = Field(default="", env="BTC_WALLET_ADDRESS")
    ltc_wallet_address: str = Field(default="", env="LTC_WALLET_ADDRESS")
    blockcypher_api_key: str = Field(default="", env="BLOCKCYPHER_API_KEY")
    blockchain_info_api_key: str = Field(default="", env="BLOCKCHAIN_INFO_API_KEY")
    
    # OSRS
    osrs_gp_rate: float = Field(default=0.50, env="OSRS_GP_RATE")
    osrs_rsn: str = Field(default="", env="OSRS_RSN")
    osrs_world: int = Field(default=302, env="OSRS_WORLD")
    osrs_trade_location: str = Field(default="Grand Exchange", env="OSRS_TRADE_LOCATION")
    
    # Payment Configuration
    payment_confirmation_blocks: int = Field(default=3, env="PAYMENT_CONFIRMATION_BLOCKS")
    payment_timeout_minutes: int = Field(default=30, env="PAYMENT_TIMEOUT_MINUTES")
    
    # Ngrok
    ngrok_auth_token: str = Field(default="", env="NGROK_AUTH_TOKEN")
    ngrok_domain: str = Field(default="", env="NGROK_DOMAIN")
    
    # Encryption
    encryption_key: str = Field(default="", env="ENCRYPTION_KEY")
    
    # Webhooks
    payment_webhook_url: str = Field(default="", env="PAYMENT_WEBHOOK_URL")
    blockcypher_webhook_token: str = Field(default="", env="BLOCKCYPHER_WEBHOOK_TOKEN")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/bot.log", env="LOG_FILE")
    
    # RuneLite Plugin
    runelite_plugin_host: str = Field(default="localhost", env="RUNELITE_PLUGIN_HOST")
    runelite_plugin_port: int = Field(default=9001, env="RUNELITE_PLUGIN_PORT")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=5, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    # Development
    dev_mode: bool = Field(default=True, env="DEV_MODE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class EncryptionManager:
    """Manage encryption and decryption of sensitive data."""
    
    def __init__(self, key: Optional[str] = None):
        """Initialize encryption manager.
        
        Args:
            key: Encryption key. If None, loads from environment.
        """
        if key is None:
            key = os.getenv("ENCRYPTION_KEY", "")
        
        if not key:
            # Generate a new key if none exists
            key = Fernet.generate_key().decode()
            print(f"Generated new encryption key: {key}")
            print("Save this to your .env file as ENCRYPTION_KEY")
        
        self.cipher = Fernet(key.encode() if isinstance(key, str) else key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data.
        
        Args:
            data: String to encrypt
            
        Returns:
            Encrypted string
        """
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt encrypted string.
        
        Args:
            encrypted_data: Encrypted string
            
        Returns:
            Decrypted string
        """
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key.
        
        Returns:
            New encryption key
        """
        return Fernet.generate_key().decode()


# Global settings instance
settings = Settings()

# Global encryption manager
encryption_manager = EncryptionManager()
