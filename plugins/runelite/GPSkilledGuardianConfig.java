package com.gpskilled.guardian;

import net.runelite.client.config.Config;
import net.runelite.client.config.ConfigGroup;
import net.runelite.client.config.ConfigItem;

/**
 * Configuration for GPSkilledGuardian plugin
 */
@ConfigGroup("gpskilledguardian")
public interface GPSkilledGuardianConfig extends Config
{
	@ConfigItem(
		keyName = "enabled",
		name = "Enable Plugin",
		description = "Enable the GPSkilled Guardian automation plugin"
	)
	default boolean enabled()
	{
		return true;
	}

	@ConfigItem(
		keyName = "serverPort",
		name = "Server Port",
		description = "Port for the HTTP server to listen on"
	)
	default int serverPort()
	{
		return 9001;
	}

	@ConfigItem(
		keyName = "autoAcceptTrades",
		name = "Auto Accept Trades",
		description = "Automatically accept trades from authorized users"
	)
	default boolean autoAcceptTrades()
	{
		return false;
	}

	@ConfigItem(
		keyName = "authorizedDiscordIds",
		name = "Authorized Discord IDs",
		description = "Comma-separated list of Discord IDs authorized to trigger trades"
	)
	default String authorizedDiscordIds()
	{
		return "";
	}

	@ConfigItem(
		keyName = "enableLogging",
		name = "Enable Logging",
		description = "Enable detailed logging for debugging"
	)
	default boolean enableLogging()
	{
		return true;
	}

	@ConfigItem(
		keyName = "screenshotTrades",
		name = "Screenshot Trades",
		description = "Automatically take screenshots of completed trades"
	)
	default boolean screenshotTrades()
	{
		return true;
	}
}
