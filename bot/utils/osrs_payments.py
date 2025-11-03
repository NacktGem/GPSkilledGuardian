"""OSRS GP payment and trade automation utilities."""
import asyncio
import aiohttp
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from config import settings
import logging

logger = logging.getLogger(__name__)


class OSRSGPPaymentProcessor:
    """OSRS Gold Pieces payment processing."""
    
    def __init__(self, gp_rate: float):
        """Initialize OSRS GP payment processor.
        
        Args:
            gp_rate: USD per million GP
        """
        self.gp_rate = gp_rate
    
    def calculate_gp_amount(self, usd_amount: float) -> float:
        """Calculate GP amount from USD.
        
        Args:
            usd_amount: Amount in USD
            
        Returns:
            Amount in GP (millions)
        """
        return (usd_amount / self.gp_rate) * 1_000_000
    
    def calculate_usd_amount(self, gp_amount: float) -> float:
        """Calculate USD amount from GP.
        
        Args:
            gp_amount: Amount in GP
            
        Returns:
            Amount in USD
        """
        return (gp_amount / 1_000_000) * self.gp_rate
    
    async def validate_rsn(self, rsn: str) -> bool:
        """Validate RuneScape Name exists.
        
        Args:
            rsn: RuneScape Name
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Using OSRS Hiscores API to validate RSN
            async with aiohttp.ClientSession() as session:
                url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={rsn}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        # If we get data back, the RSN exists
                        data = await response.text()
                        return len(data) > 0
                    else:
                        return False
        except Exception as e:
            logger.error(f"Error validating RSN {rsn}: {e}")
            return False
    
    async def get_player_stats(self, rsn: str) -> Optional[Dict[str, Any]]:
        """Get player stats from OSRS Hiscores.
        
        Args:
            rsn: RuneScape Name
            
        Returns:
            Player stats dict or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={rsn}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.text()
                        lines = data.strip().split('\n')
                        
                        # Parse overall stats (first line)
                        if lines:
                            overall = lines[0].split(',')
                            return {
                                "rsn": rsn,
                                "rank": int(overall[0]) if overall[0] != '-1' else None,
                                "level": int(overall[1]) if len(overall) > 1 else None,
                                "xp": int(overall[2]) if len(overall) > 2 else None
                            }
                    return None
        except Exception as e:
            logger.error(f"Error getting player stats for {rsn}: {e}")
            return None


class RuneLitePluginClient:
    """Client for communicating with RuneLite plugin."""
    
    def __init__(self, host: str, port: int):
        """Initialize RuneLite plugin client.
        
        Args:
            host: Plugin host
            port: Plugin port
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
    
    async def is_connected(self) -> bool:
        """Check if RuneLite plugin is connected.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/status"
                timeout = aiohttp.ClientTimeout(total=5)
                
                async with session.get(url, timeout=timeout) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"RuneLite plugin not connected: {e}")
            return False
    
    async def get_current_world(self) -> Optional[int]:
        """Get current world number.
        
        Returns:
            World number or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/world"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("world")
                    return None
        except Exception as e:
            logger.error(f"Error getting current world: {e}")
            return None
    
    async def hop_world(self, world: int) -> bool:
        """Hop to a specific world.
        
        Args:
            world: World number to hop to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/world/hop"
                payload = {"world": world}
                
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error hopping to world {world}: {e}")
            return False
    
    async def send_trade_request(self, rsn: str) -> bool:
        """Send trade request to player.
        
        Args:
            rsn: RuneScape Name to trade with
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/trade/request"
                payload = {"rsn": rsn}
                
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error sending trade request to {rsn}: {e}")
            return False
    
    async def offer_gp(self, amount: int) -> bool:
        """Offer GP in trade window.
        
        Args:
            amount: Amount of GP to offer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/trade/offer"
                payload = {"amount": amount}
                
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error offering {amount} GP: {e}")
            return False
    
    async def accept_trade(self) -> bool:
        """Accept current trade.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/trade/accept"
                
                async with session.post(url) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error accepting trade: {e}")
            return False
    
    async def get_trade_status(self) -> Optional[Dict[str, Any]]:
        """Get current trade status.
        
        Returns:
            Trade status dict or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/trade/status"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            logger.error(f"Error getting trade status: {e}")
            return None
    
    async def take_screenshot(self) -> Optional[bytes]:
        """Take screenshot of game client.
        
        Returns:
            Screenshot bytes or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/screenshot"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
                    return None
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None
    
    async def send_message(self, message: str, public: bool = False) -> bool:
        """Send chat message.
        
        Args:
            message: Message to send
            public: If True, sends public chat, else private message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/chat/send"
                payload = {"message": message, "public": public}
                
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False


class OSRSTradeAutomation:
    """Automated OSRS trading system."""
    
    def __init__(self, plugin_client: RuneLitePluginClient, gp_processor: OSRSGPPaymentProcessor):
        """Initialize trade automation.
        
        Args:
            plugin_client: RuneLite plugin client
            gp_processor: GP payment processor
        """
        self.plugin = plugin_client
        self.gp_processor = gp_processor
    
    async def execute_trade(
        self,
        rsn: str,
        gp_amount: int,
        world: int,
        location: str
    ) -> Tuple[bool, str]:
        """Execute automated trade.
        
        Args:
            rsn: RuneScape Name to trade with
            gp_amount: Amount of GP to trade
            world: World to trade on
            location: Location description
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if plugin is connected
            if not await self.plugin.is_connected():
                return False, "RuneLite plugin is not connected"
            
            # Hop to the specified world
            logger.info(f"Hopping to world {world}")
            if not await self.plugin.hop_world(world):
                return False, f"Failed to hop to world {world}"
            
            # Wait for world hop
            await asyncio.sleep(5)
            
            # Send trade request
            logger.info(f"Sending trade request to {rsn}")
            if not await self.plugin.send_trade_request(rsn):
                return False, f"Failed to send trade request to {rsn}"
            
            # Wait for trade window to open
            await asyncio.sleep(3)
            
            # Offer GP
            logger.info(f"Offering {gp_amount} GP")
            if not await self.plugin.offer_gp(gp_amount):
                return False, "Failed to offer GP in trade"
            
            # Wait for user to accept
            logger.info("Waiting for trade acceptance...")
            max_wait = 300  # 5 minutes
            wait_time = 0
            
            while wait_time < max_wait:
                status = await self.plugin.get_trade_status()
                if status and status.get("status") == "completed":
                    # Take screenshot of completed trade
                    screenshot = await self.plugin.take_screenshot()
                    if screenshot:
                        logger.info("Trade completed and screenshot taken")
                    
                    return True, "Trade completed successfully"
                
                await asyncio.sleep(5)
                wait_time += 5
            
            return False, "Trade timed out waiting for acceptance"
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False, f"Trade error: {str(e)}"
