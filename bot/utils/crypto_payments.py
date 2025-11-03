"""Cryptocurrency payment processing utilities."""
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from config import settings
from bot.models import Payment, PaymentStatus, PaymentType
import logging

logger = logging.getLogger(__name__)


class BitcoinPaymentProcessor:
    """Bitcoin payment processing using BlockCypher API."""
    
    BASE_URL = "https://api.blockcypher.com/v1/btc/main"
    
    def __init__(self, api_key: str):
        """Initialize Bitcoin payment processor.
        
        Args:
            api_key: BlockCypher API key
        """
        self.api_key = api_key
    
    async def create_payment_address(self) -> Optional[Dict[str, Any]]:
        """Create a new payment address for receiving Bitcoin.
        
        Returns:
            Dict containing address info or None on error
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/addrs"
                params = {"token": self.api_key}
                
                async with session.post(url, params=params) as response:
                    if response.status == 201:
                        data = await response.json()
                        return {
                            "address": data.get("address"),
                            "private": data.get("private"),
                            "public": data.get("public")
                        }
                    else:
                        logger.error(f"Failed to create BTC address: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error creating BTC payment address: {e}")
            return None
    
    async def check_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Check Bitcoin transaction status.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction details or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/txs/{tx_hash}"
                params = {"token": self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to check BTC transaction: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error checking BTC transaction: {e}")
            return None
    
    async def get_address_balance(self, address: str) -> Optional[float]:
        """Get balance of a Bitcoin address.
        
        Args:
            address: Bitcoin address
            
        Returns:
            Balance in BTC or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/addrs/{address}/balance"
                params = {"token": self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Convert from satoshis to BTC
                        return data.get("balance", 0) / 100000000
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error getting BTC balance: {e}")
            return None
    
    async def create_webhook(self, address: str, callback_url: str) -> Optional[str]:
        """Create a webhook for monitoring address.
        
        Args:
            address: Bitcoin address to monitor
            callback_url: URL to receive webhook notifications
            
        Returns:
            Webhook ID or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/hooks"
                params = {"token": self.api_key}
                payload = {
                    "event": "tx-confirmation",
                    "address": address,
                    "url": callback_url,
                    "confirmations": settings.payment_confirmation_blocks
                }
                
                async with session.post(url, params=params, json=payload) as response:
                    if response.status == 201:
                        data = await response.json()
                        return data.get("id")
                    else:
                        logger.error(f"Failed to create webhook: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return None


class LitecoinPaymentProcessor:
    """Litecoin payment processing using BlockCypher API."""
    
    BASE_URL = "https://api.blockcypher.com/v1/ltc/main"
    
    def __init__(self, api_key: str):
        """Initialize Litecoin payment processor.
        
        Args:
            api_key: BlockCypher API key
        """
        self.api_key = api_key
    
    async def create_payment_address(self) -> Optional[Dict[str, Any]]:
        """Create a new payment address for receiving Litecoin.
        
        Returns:
            Dict containing address info or None on error
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/addrs"
                params = {"token": self.api_key}
                
                async with session.post(url, params=params) as response:
                    if response.status == 201:
                        data = await response.json()
                        return {
                            "address": data.get("address"),
                            "private": data.get("private"),
                            "public": data.get("public")
                        }
                    else:
                        logger.error(f"Failed to create LTC address: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error creating LTC payment address: {e}")
            return None
    
    async def check_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Check Litecoin transaction status.
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction details or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/txs/{tx_hash}"
                params = {"token": self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to check LTC transaction: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error checking LTC transaction: {e}")
            return None
    
    async def get_address_balance(self, address: str) -> Optional[float]:
        """Get balance of a Litecoin address.
        
        Args:
            address: Litecoin address
            
        Returns:
            Balance in LTC or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.BASE_URL}/addrs/{address}/balance"
                params = {"token": self.api_key}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Convert from litoshis to LTC
                        return data.get("balance", 0) / 100000000
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error getting LTC balance: {e}")
            return None


class CryptoRateConverter:
    """Convert between USD and cryptocurrency rates."""
    
    COINBASE_API = "https://api.coinbase.com/v2/exchange-rates"
    
    @staticmethod
    async def get_btc_rate() -> Optional[float]:
        """Get current BTC to USD rate.
        
        Returns:
            BTC price in USD or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{CryptoRateConverter.COINBASE_API}?currency=BTC"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data["data"]["rates"]["USD"])
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error getting BTC rate: {e}")
            return None
    
    @staticmethod
    async def get_ltc_rate() -> Optional[float]:
        """Get current LTC to USD rate.
        
        Returns:
            LTC price in USD or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{CryptoRateConverter.COINBASE_API}?currency=LTC"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data["data"]["rates"]["USD"])
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error getting LTC rate: {e}")
            return None
    
    @staticmethod
    async def usd_to_btc(usd_amount: float) -> Optional[float]:
        """Convert USD to BTC.
        
        Args:
            usd_amount: Amount in USD
            
        Returns:
            Amount in BTC or None
        """
        rate = await CryptoRateConverter.get_btc_rate()
        if rate:
            return usd_amount / rate
        return None
    
    @staticmethod
    async def usd_to_ltc(usd_amount: float) -> Optional[float]:
        """Convert USD to LTC.
        
        Args:
            usd_amount: Amount in USD
            
        Returns:
            Amount in LTC or None
        """
        rate = await CryptoRateConverter.get_ltc_rate()
        if rate:
            return usd_amount / rate
        return None
