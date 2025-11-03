"""Moderation cog for Discord bot."""
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from typing import Optional
from bot.database import get_db_session
from bot.models import ModerationAction
from bot.utils import logger
from config import settings


class Moderation(commands.Cog):
    """Moderation commands for managing server members."""
    
    def __init__(self, bot: commands.Bot):
        """Initialize moderation cog.
        
        Args:
            bot: Discord bot instance
        """
        self.bot = bot
    
    async def log_action(
        self,
        user_id: str,
        moderator_id: str,
        action_type: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None
    ):
        """Log moderation action to database.
        
        Args:
            user_id: Target user ID
            moderator_id: Moderator user ID
            action_type: Type of action
            reason: Reason for action
            duration: Duration in minutes
        """
        async with get_db_session() as session:
            action = ModerationAction(
                user_id=user_id,
                moderator_id=moderator_id,
                action_type=action_type,
                reason=reason,
                duration=duration,
                expires_at=datetime.utcnow() + timedelta(minutes=duration) if duration else None
            )
            session.add(action)
            await session.commit()
    
    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(
        member="The member to warn",
        reason="Reason for the warning"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        """Warn a user.
        
        Args:
            interaction: Discord interaction
            member: Member to warn
            reason: Reason for warning
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Log the warning
            await self.log_action(
                user_id=str(member.id),
                moderator_id=str(interaction.user.id),
                action_type="warn",
                reason=reason
            )
            
            # Try to DM the user
            try:
                embed = discord.Embed(
                    title="⚠️ Warning",
                    description=f"You have been warned in {interaction.guild.name}",
                    color=discord.Color.yellow(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                
                await member.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Could not DM warning to {member.id}")
            
            # Respond to moderator
            embed = discord.Embed(
                title="✅ User Warned",
                description=f"{member.mention} has been warned",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{interaction.user} warned {member} for: {reason}")
            
        except Exception as e:
            logger.error(f"Error warning user: {e}")
            await interaction.followup.send(
                "❌ An error occurred while warning the user.",
                ephemeral=True
            )
    
    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.describe(
        member="The member to mute",
        duration="Duration in minutes",
        reason="Reason for the mute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        duration: int,
        reason: str = "No reason provided"
    ):
        """Mute a user for a specified duration.
        
        Args:
            interaction: Discord interaction
            member: Member to mute
            duration: Duration in minutes
            reason: Reason for mute
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Calculate timeout duration
            timeout_until = datetime.utcnow() + timedelta(minutes=duration)
            
            # Apply timeout
            await member.timeout(timeout_until, reason=reason)
            
            # Log the action
            await self.log_action(
                user_id=str(member.id),
                moderator_id=str(interaction.user.id),
                action_type="mute",
                reason=reason,
                duration=duration
            )
            
            # Try to DM the user
            try:
                embed = discord.Embed(
                    title="🔇 Muted",
                    description=f"You have been muted in {interaction.guild.name}",
                    color=discord.Color.orange(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                
                await member.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Could not DM mute notification to {member.id}")
            
            # Respond to moderator
            embed = discord.Embed(
                title="✅ User Muted",
                description=f"{member.mention} has been muted",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{interaction.user} muted {member} for {duration}m: {reason}")
            
        except Exception as e:
            logger.error(f"Error muting user: {e}")
            await interaction.followup.send(
                "❌ An error occurred while muting the user.",
                ephemeral=True
            )
    
    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.describe(
        member="The member to unmute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        """Unmute a user.
        
        Args:
            interaction: Discord interaction
            member: Member to unmute
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Remove timeout
            await member.timeout(None)
            
            # Respond to moderator
            embed = discord.Embed(
                title="✅ User Unmuted",
                description=f"{member.mention} has been unmuted",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{interaction.user} unmuted {member}")
            
        except Exception as e:
            logger.error(f"Error unmuting user: {e}")
            await interaction.followup.send(
                "❌ An error occurred while unmuting the user.",
                ephemeral=True
            )
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided"
    ):
        """Kick a user from the server.
        
        Args:
            interaction: Discord interaction
            member: Member to kick
            reason: Reason for kick
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Try to DM the user before kicking
            try:
                embed = discord.Embed(
                    title="👢 Kicked",
                    description=f"You have been kicked from {interaction.guild.name}",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                
                await member.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Could not DM kick notification to {member.id}")
            
            # Log the action
            await self.log_action(
                user_id=str(member.id),
                moderator_id=str(interaction.user.id),
                action_type="kick",
                reason=reason
            )
            
            # Kick the user
            await member.kick(reason=reason)
            
            # Respond to moderator
            embed = discord.Embed(
                title="✅ User Kicked",
                description=f"{member.mention} has been kicked",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{interaction.user} kicked {member} for: {reason}")
            
        except Exception as e:
            logger.error(f"Error kicking user: {e}")
            await interaction.followup.send(
                "❌ An error occurred while kicking the user.",
                ephemeral=True
            )
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        member="The member to ban",
        reason="Reason for the ban",
        delete_messages="Delete messages from the last N days (0-7)"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided",
        delete_messages: int = 0
    ):
        """Ban a user from the server.
        
        Args:
            interaction: Discord interaction
            member: Member to ban
            reason: Reason for ban
            delete_messages: Days of messages to delete
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Try to DM the user before banning
            try:
                embed = discord.Embed(
                    title="🔨 Banned",
                    description=f"You have been banned from {interaction.guild.name}",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                
                await member.send(embed=embed)
            except discord.Forbidden:
                logger.warning(f"Could not DM ban notification to {member.id}")
            
            # Log the action
            await self.log_action(
                user_id=str(member.id),
                moderator_id=str(interaction.user.id),
                action_type="ban",
                reason=reason
            )
            
            # Ban the user
            await member.ban(
                reason=reason,
                delete_message_days=min(delete_messages, 7)
            )
            
            # Respond to moderator
            embed = discord.Embed(
                title="✅ User Banned",
                description=f"{member.mention} has been banned",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{interaction.user} banned {member} for: {reason}")
            
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            await interaction.followup.send(
                "❌ An error occurred while banning the user.",
                ephemeral=True
            )
    
    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The user ID to unban"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str
    ):
        """Unban a user from the server.
        
        Args:
            interaction: Discord interaction
            user_id: User ID to unban
        """
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get user object
            user = await self.bot.fetch_user(int(user_id))
            
            # Unban the user
            await interaction.guild.unban(user)
            
            # Respond to moderator
            embed = discord.Embed(
                title="✅ User Unbanned",
                description=f"{user.mention} has been unbanned",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"{interaction.user} unbanned {user}")
            
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            await interaction.followup.send(
                "❌ An error occurred while unbanning the user.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Setup function for loading the cog.
    
    Args:
        bot: Discord bot instance
    """
    await bot.add_cog(Moderation(bot))
