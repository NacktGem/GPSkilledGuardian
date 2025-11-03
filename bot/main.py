"""Main Discord bot for GPSkilledGuardian."""
import discord
from discord.ext import commands
import asyncio
from pathlib import Path
from bot.database import init_db
from bot.utils import logger
from config import settings


class GPSkilledGuardian(commands.Bot):
    """Main bot class."""
    
    def __init__(self):
        """Initialize the bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        """Setup hook called when bot starts."""
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        
        # Load cogs
        logger.info("Loading cogs...")
        cogs_dir = Path(__file__).parent / "cogs"
        
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
            
            cog_name = f"bot.cogs.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info(f"Loaded cog: {cog_name}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog_name}: {e}")
        
        # Sync commands
        logger.info("Syncing application commands...")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for payments | /pay"
            )
        )
        
        logger.info("Bot is ready!")
    
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle command errors.
        
        Args:
            ctx: Command context
            error: Error that occurred
        """
        if isinstance(error, commands.CommandNotFound):
            return
        
        logger.error(f"Command error in {ctx.command}: {error}")
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
        else:
            await ctx.send("❌ An error occurred while executing the command.")
    
    async def on_error(self, event: str, *args, **kwargs):
        """Handle general errors.
        
        Args:
            event: Event name
            args: Event args
            kwargs: Event kwargs
        """
        logger.error(f"Error in event {event}", exc_info=True)


async def main():
    """Main function to run the bot."""
    # Check if token is set
    if not settings.discord_token:
        logger.error("DISCORD_TOKEN not set in environment variables")
        return
    
    # Create and run bot
    bot = GPSkilledGuardian()
    
    try:
        async with bot:
            await bot.start(settings.discord_token)
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
    except Exception as e:
        logger.error(f"Error running bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())
