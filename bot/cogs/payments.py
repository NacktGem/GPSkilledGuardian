"""Payment cog for Discord bot."""
import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from bot.database import get_db_session
from bot.models import Payment, PaymentStatus, PaymentType, User, OSRSTrade
from bot.utils import logger
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
from config import settings
import asyncio


class Payments(commands.Cog):
    """Payment processing and role assignment."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize payments cog.
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
        
        # Initialize payment processors
        self.btc_processor = BitcoinPaymentProcessor(settings.blockcypher_api_key)
        self.ltc_processor = LitecoinPaymentProcessor(settings.blockcypher_api_key)
        self.osrs_processor = OSRSGPPaymentProcessor(settings.osrs_gp_rate)
        
        # Initialize RuneLite client
        self.runelite_client = RuneLitePluginClient(
            settings.runelite_plugin_host,
            settings.runelite_plugin_port
        )
        self.trade_automation = OSRSTradeAutomation(
            self.runelite_client,
            self.osrs_processor
        )
        
        # Start payment monitoring
        self.payment_monitor.start()
    
    def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.payment_monitor.cancel()
    
    @app_commands.command(name="pay", description="Initiate a payment for access")
    @app_commands.describe(
        payment_type="Type of payment (btc, ltc, osrs_gp)",
        amount_usd="Amount in USD"
    )
    async def pay(
        self,
        interaction: discord.Interaction,
        payment_type: str,
        amount_usd: float
    ):
        """Initiate a payment.
        
        Args:
            interaction: Discord interaction
            payment_type: Payment type (btc, ltc, osrs_gp)
            amount_usd: Amount in USD
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validate payment type
            payment_type_lower = payment_type.lower()
            if payment_type_lower not in ["btc", "ltc", "osrs_gp"]:
                await interaction.followup.send(
                    "❌ Invalid payment type. Choose from: btc, ltc, osrs_gp",
                    ephemeral=True
                )
                return
            
            # Create payment record
            async with get_db_session() as session:
                # Get or create user
                result = await session.execute(
                    select(User).where(User.discord_id == str(interaction.user.id))
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    user = User(
                        discord_id=str(interaction.user.id),
                        username=str(interaction.user)
                    )
                    session.add(user)
                    await session.flush()
                
                # Create payment
                payment = Payment(
                    user_id=str(interaction.user.id),
                    username=str(interaction.user),
                    payment_type=PaymentType[payment_type_lower.upper()],
                    amount_usd=amount_usd,
                    expires_at=datetime.utcnow() + timedelta(minutes=settings.payment_timeout_minutes)
                )
                
                # Handle different payment types
                if payment_type_lower == "btc":
                    # Convert USD to BTC
                    btc_amount = await CryptoRateConverter.usd_to_btc(amount_usd)
                    if not btc_amount:
                        await interaction.followup.send(
                            "❌ Failed to get BTC conversion rate. Please try again.",
                            ephemeral=True
                        )
                        return
                    
                    payment.amount_crypto = btc_amount
                    payment.wallet_address = settings.btc_wallet_address
                    
                    embed = discord.Embed(
                        title="💳 Bitcoin Payment",
                        description="Please send Bitcoin to the address below",
                        color=discord.Color.gold(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Amount (USD)", value=f"${amount_usd:.2f}", inline=True)
                    embed.add_field(name="Amount (BTC)", value=f"{btc_amount:.8f} BTC", inline=True)
                    embed.add_field(name="Payment Address", value=f"```{settings.btc_wallet_address}```", inline=False)
                    embed.add_field(
                        name="Confirmations Required",
                        value=str(settings.payment_confirmation_blocks),
                        inline=True
                    )
                    embed.add_field(
                        name="Expires In",
                        value=f"{settings.payment_timeout_minutes} minutes",
                        inline=True
                    )
                    embed.set_footer(text=f"Payment ID: {payment.id}")
                
                elif payment_type_lower == "ltc":
                    # Convert USD to LTC
                    ltc_amount = await CryptoRateConverter.usd_to_ltc(amount_usd)
                    if not ltc_amount:
                        await interaction.followup.send(
                            "❌ Failed to get LTC conversion rate. Please try again.",
                            ephemeral=True
                        )
                        return
                    
                    payment.amount_crypto = ltc_amount
                    payment.wallet_address = settings.ltc_wallet_address
                    
                    embed = discord.Embed(
                        title="💳 Litecoin Payment",
                        description="Please send Litecoin to the address below",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Amount (USD)", value=f"${amount_usd:.2f}", inline=True)
                    embed.add_field(name="Amount (LTC)", value=f"{ltc_amount:.8f} LTC", inline=True)
                    embed.add_field(name="Payment Address", value=f"```{settings.ltc_wallet_address}```", inline=False)
                    embed.add_field(
                        name="Confirmations Required",
                        value=str(settings.payment_confirmation_blocks),
                        inline=True
                    )
                    embed.add_field(
                        name="Expires In",
                        value=f"{settings.payment_timeout_minutes} minutes",
                        inline=True
                    )
                    embed.set_footer(text=f"Payment ID: {payment.id}")
                
                elif payment_type_lower == "osrs_gp":
                    # Calculate GP amount
                    gp_amount = self.osrs_processor.calculate_gp_amount(amount_usd)
                    payment.amount_gp = gp_amount
                    
                    embed = discord.Embed(
                        title="🪙 OSRS GP Payment",
                        description="Please provide your RuneScape Name to initiate trade",
                        color=discord.Color.orange(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Amount (USD)", value=f"${amount_usd:.2f}", inline=True)
                    embed.add_field(name="Amount (GP)", value=f"{gp_amount:,.0f} GP", inline=True)
                    embed.add_field(name="Rate", value=f"${settings.osrs_gp_rate}/M", inline=True)
                    embed.add_field(name="World", value=str(settings.osrs_world), inline=True)
                    embed.add_field(name="Location", value=settings.osrs_trade_location, inline=True)
                    embed.add_field(
                        name="Next Step",
                        value="Use `/setrsn <your_rsn>` to set your RuneScape name",
                        inline=False
                    )
                    embed.set_footer(text=f"Payment ID: {payment.id}")
                
                session.add(payment)
                await session.commit()
                
                await interaction.followup.send(embed=embed, ephemeral=True)
                logger.info(f"Payment initiated: {payment.id} - {interaction.user} - {payment_type_lower} - ${amount_usd}")
        
        except Exception as e:
            logger.error(f"Error initiating payment: {e}")
            await interaction.followup.send(
                "❌ An error occurred while initiating payment.",
                ephemeral=True
            )
    
    @app_commands.command(name="setrsn", description="Set your RuneScape Name for OSRS GP payments")
    @app_commands.describe(rsn="Your RuneScape Name")
    async def setrsn(
        self,
        interaction: discord.Interaction,
        rsn: str
    ):
        """Set RuneScape Name for user.
        
        Args:
            interaction: Discord interaction
            rsn: RuneScape Name
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validate RSN
            if not await self.osrs_processor.validate_rsn(rsn):
                await interaction.followup.send(
                    f"❌ Could not find RuneScape account: {rsn}",
                    ephemeral=True
                )
                return
            
            # Update user record
            async with get_db_session() as session:
                result = await session.execute(
                    select(User).where(User.discord_id == str(interaction.user.id))
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    user = User(
                        discord_id=str(interaction.user.id),
                        username=str(interaction.user),
                        osrs_rsn=rsn
                    )
                    session.add(user)
                else:
                    user.osrs_rsn = rsn
                
                await session.commit()
            
            # Check for pending OSRS payments
            async with get_db_session() as session:
                result = await session.execute(
                    select(Payment).where(
                        Payment.user_id == str(interaction.user.id),
                        Payment.payment_type == PaymentType.OSRS_GP,
                        Payment.status == PaymentStatus.PENDING
                    )
                )
                pending_payment = result.scalar_one_or_none()
                
                if pending_payment:
                    # Create trade record
                    trade = OSRSTrade(
                        payment_id=pending_payment.id,
                        user_id=str(interaction.user.id),
                        rsn=rsn,
                        gp_amount=pending_payment.amount_gp,
                        world=settings.osrs_world,
                        location=settings.osrs_trade_location
                    )
                    session.add(trade)
                    await session.commit()
                    
                    embed = discord.Embed(
                        title="✅ RSN Set & Trade Initiated",
                        description=f"Your RSN has been set to: **{rsn}**",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="World", value=str(settings.osrs_world), inline=True)
                    embed.add_field(name="Location", value=settings.osrs_trade_location, inline=True)
                    embed.add_field(
                        name="Instructions",
                        value=f"Please log into World {settings.osrs_world} and wait at {settings.osrs_trade_location}. "
                              f"You will receive a trade request from: **{settings.osrs_rsn}**",
                        inline=False
                    )
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    logger.info(f"OSRS trade initiated for {interaction.user} ({rsn})")
                else:
                    await interaction.followup.send(
                        f"✅ RuneScape Name set to: **{rsn}**",
                        ephemeral=True
                    )
        
        except Exception as e:
            logger.error(f"Error setting RSN: {e}")
            await interaction.followup.send(
                "❌ An error occurred while setting your RSN.",
                ephemeral=True
            )
    
    @app_commands.command(name="checkpayment", description="Check your payment status")
    async def checkpayment(self, interaction: discord.Interaction):
        """Check payment status.
        
        Args:
            interaction: Discord interaction
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            async with get_db_session() as session:
                result = await session.execute(
                    select(Payment).where(
                        Payment.user_id == str(interaction.user.id)
                    ).order_by(Payment.created_at.desc())
                )
                payments = result.scalars().all()
                
                if not payments:
                    await interaction.followup.send(
                        "❌ No payments found.",
                        ephemeral=True
                    )
                    return
                
                embed = discord.Embed(
                    title="💰 Your Payments",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                
                for payment in payments[:5]:  # Show last 5
                    status_emoji = {
                        PaymentStatus.PENDING: "⏳",
                        PaymentStatus.CONFIRMING: "🔄",
                        PaymentStatus.COMPLETED: "✅",
                        PaymentStatus.EXPIRED: "❌",
                        PaymentStatus.FAILED: "❌"
                    }
                    
                    value = (
                        f"Status: {status_emoji.get(payment.status, '❓')} {payment.status.value}\n"
                        f"Amount: ${payment.amount_usd:.2f}\n"
                        f"Created: {payment.created_at.strftime('%Y-%m-%d %H:%M UTC')}"
                    )
                    
                    if payment.status == PaymentStatus.CONFIRMING:
                        value += f"\nConfirmations: {payment.confirmations}/{settings.payment_confirmation_blocks}"
                    
                    embed.add_field(
                        name=f"Payment #{payment.id} - {payment.payment_type.value.upper()}",
                        value=value,
                        inline=False
                    )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error checking payment: {e}")
            await interaction.followup.send(
                "❌ An error occurred while checking payments.",
                ephemeral=True
            )
    
    @tasks.loop(minutes=1)
    async def payment_monitor(self):
        """Monitor pending payments and process them."""
        try:
            async with get_db_session() as session:
                # Check for expired payments
                result = await session.execute(
                    select(Payment).where(
                        Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.CONFIRMING]),
                        Payment.expires_at < datetime.utcnow()
                    )
                )
                expired_payments = result.scalars().all()
                
                for payment in expired_payments:
                    payment.status = PaymentStatus.EXPIRED
                    logger.info(f"Payment {payment.id} expired")
                
                await session.commit()
        
        except Exception as e:
            logger.error(f"Error in payment monitor: {e}")
    
    @payment_monitor.before_loop
    async def before_payment_monitor(self):
        """Wait for bot to be ready before starting monitor."""
        await self.bot.wait_until_ready()
    
    async def assign_payment_role(self, user_id: str):
        """Assign payment role to user.
        
        Args:
            user_id: Discord user ID
        """
        try:
            guild = self.bot.get_guild(settings.discord_guild_id)
            if not guild:
                logger.error(f"Guild {settings.discord_guild_id} not found")
                return
            
            member = guild.get_member(int(user_id))
            if not member:
                logger.error(f"Member {user_id} not found")
                return
            
            role = guild.get_role(settings.discord_payment_role_id)
            if not role:
                logger.error(f"Role {settings.discord_payment_role_id} not found")
                return
            
            await member.add_roles(role)
            logger.info(f"Assigned payment role to {member}")
            
            # Update user record
            async with get_db_session() as session:
                result = await session.execute(
                    select(User).where(User.discord_id == user_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    user.has_paid_role = True
                    await session.commit()
        
        except Exception as e:
            logger.error(f"Error assigning payment role: {e}")


async def setup(bot: commands.Bot):
    """Setup function for loading the cog.
    
    Args:
        bot: Discord bot instance
    """
    await bot.add_cog(Payments(bot))
