"""Bot utilities package."""
from bot.utils.logger import setup_logger, logger
from bot.utils.crypto_payments import (
    BitcoinPaymentProcessor,
    LitecoinPaymentProcessor,
    CryptoRateConverter
)
from bot.utils.osrs_payments import (
    OSRSGPPaymentProcessor,
    RuneLitePluginClient,
    OSRSTradeAutomation
)

__all__ = [
    "setup_logger",
    "logger",
    "BitcoinPaymentProcessor",
    "LitecoinPaymentProcessor",
    "CryptoRateConverter",
    "OSRSGPPaymentProcessor",
    "RuneLitePluginClient",
    "OSRSTradeAutomation"
]
