# RuneLite Plugin Documentation

## Overview

The GPSkilledGuardian RuneLite plugin provides automated trading capabilities for OSRS GP payments. It exposes a local HTTP server that the Discord bot can communicate with to execute trades automatically.

## Architecture

The plugin consists of:
- **GPSkilledGuardianPlugin.java** - Main plugin class
- **GPSkilledGuardianConfig.java** - Configuration interface
- **HttpServer.java** - HTTP server for external communication (to be implemented)

## Features

1. **World Hopping** - Automatically hop to specified worlds
2. **Trade Requests** - Send trade requests to players by RSN
3. **GP Offering** - Offer GP in the trade window
4. **Trade Acceptance** - Accept trades programmatically
5. **Screenshot Capture** - Take screenshots of completed trades
6. **Chat Messaging** - Send messages in chat
7. **Trade Status Monitoring** - Monitor trade status

## HTTP Server API

The plugin exposes a local HTTP server on port 9001 (configurable).

### Endpoints

#### `GET /status`
Check if the plugin is connected and ready.

**Response:**
```json
{
  "status": "connected",
  "logged_in": true,
  "world": 302
}
```

#### `GET /world`
Get the current world number.

**Response:**
```json
{
  "world": 302
}
```

#### `POST /world/hop`
Hop to a specific world.

**Request:**
```json
{
  "world": 302
}
```

**Response:**
```json
{
  "success": true,
  "world": 302
}
```

#### `POST /trade/request`
Send a trade request to a player.

**Request:**
```json
{
  "rsn": "PlayerName"
}
```

**Response:**
```json
{
  "success": true,
  "rsn": "PlayerName"
}
```

#### `POST /trade/offer`
Offer GP in the trade window.

**Request:**
```json
{
  "amount": 20000000
}
```

**Response:**
```json
{
  "success": true,
  "amount": 20000000
}
```

#### `POST /trade/accept`
Accept the current trade.

**Response:**
```json
{
  "success": true
}
```

#### `GET /trade/status`
Get the current trade status.

**Response:**
```json
{
  "status": "in_progress",
  "player": "PlayerName",
  "offered_amount": 20000000
}
```

or

```json
{
  "status": "no_trade"
}
```

#### `GET /screenshot`
Take a screenshot of the game client.

**Response:**
Binary image data (PNG format)

#### `POST /chat/send`
Send a chat message.

**Request:**
```json
{
  "message": "Trade complete!",
  "public": false
}
```

**Response:**
```json
{
  "success": true
}
```

## Installation

### Prerequisites

- RuneLite client
- Java 11+
- Gradle (for building)

### Building from Source

1. Clone the RuneLite repository:
   ```bash
   git clone https://github.com/runelite/runelite.git
   cd runelite
   ```

2. Create plugin directory:
   ```bash
   mkdir -p runelite-client/src/main/java/net/runelite/client/plugins/gpskilledguardian
   ```

3. Copy plugin files:
   ```bash
   cp GPSkilledGuardianPlugin.java runelite-client/src/main/java/net/runelite/client/plugins/gpskilledguardian/
   cp GPSkilledGuardianConfig.java runelite-client/src/main/java/net/runelite/client/plugins/gpskilledguardian/
   ```

4. Build the plugin:
   ```bash
   ./gradlew runelite-client:build
   ```

5. The plugin will be built into the RuneLite client.

### Installation via Plugin Hub

(If submitted to Plugin Hub)

1. Open RuneLite
2. Click the Plugin Hub icon
3. Search for "GPSkilled Guardian"
4. Click Install

## Configuration

### Plugin Settings

Access settings in RuneLite:
1. Click the Configuration icon (wrench)
2. Search for "GPSkilled Guardian"
3. Configure options:

- **Enable Plugin**: Turn the plugin on/off
- **Server Port**: Port for HTTP server (default: 9001)
- **Auto Accept Trades**: Automatically accept trades (not recommended)
- **Authorized Discord IDs**: Comma-separated Discord IDs allowed to trigger trades
- **Enable Logging**: Enable detailed logging for debugging
- **Screenshot Trades**: Automatically screenshot completed trades

## Security

### Important Security Considerations

1. **Local Only**: The HTTP server only listens on localhost (127.0.0.1)
2. **No Authentication**: Currently no authentication on endpoints
3. **Authorized Users**: Use the "Authorized Discord IDs" setting to restrict who can trigger trades
4. **Manual Acceptance**: Consider disabling "Auto Accept Trades" for safety
5. **Logging**: Enable logging to track all trade requests

### Best Practices

- Only run the plugin when actively trading
- Monitor logs for suspicious activity
- Never share your Discord ID with untrusted parties
- Disable the plugin when not in use
- Use the plugin on a dedicated trading account

## Usage

### Starting the Plugin

1. Start RuneLite
2. Log into OSRS
3. Enable the plugin in RuneLite settings
4. Plugin will start HTTP server automatically
5. Check logs to confirm server is running

### Making a Trade

The Discord bot will automatically:
1. Connect to the plugin via HTTP
2. Check plugin status
3. Hop to the trading world
4. Send trade request
5. Offer GP
6. Wait for acceptance
7. Take screenshot

Your role:
1. Be logged in and at the trading location
2. Accept the trade when prompted
3. Verify the trade is correct

## Troubleshooting

### Plugin won't start
- Check Java version is 11+
- Verify port 9001 is not in use
- Check RuneLite console for errors

### HTTP server not accessible
- Verify plugin is enabled
- Check firewall isn't blocking port 9001
- Ensure you're connecting to localhost
- Check server port in settings

### Trades not executing
- Verify you're logged in
- Check you're at the correct location
- Ensure target player is nearby
- Check trade window isn't already open

### Screenshots not saving
- Verify screenshot directory permissions
- Check disk space
- Enable logging to see errors

## Development

### HTTP Server Implementation

The `HttpServer.java` class needs to be implemented. Here's a basic structure:

```java
import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;

public class HttpServer {
    private HttpServer server;
    private GPSkilledGuardianPlugin plugin;
    private Client client;
    private int port;
    
    public HttpServer(GPSkilledGuardianPlugin plugin, Client client, int port) {
        this.plugin = plugin;
        this.client = client;
        this.port = port;
    }
    
    public void start() throws IOException {
        server = HttpServer.create(new InetSocketAddress("localhost", port), 0);
        
        // Register endpoints
        server.createContext("/status", new StatusHandler());
        server.createContext("/world", new WorldHandler());
        server.createContext("/trade/request", new TradeRequestHandler());
        // ... more handlers
        
        server.setExecutor(null);
        server.start();
    }
    
    public void stop() {
        if (server != null) {
            server.stop(0);
        }
    }
    
    // Handler implementations...
}
```

### Testing

Test the plugin locally:

```bash
# Check status
curl http://localhost:9001/status

# Get world
curl http://localhost:9001/world

# Send trade request
curl -X POST http://localhost:9001/trade/request \
  -H "Content-Type: application/json" \
  -d '{"rsn":"PlayerName"}'
```

## Future Enhancements

- [ ] Add authentication via API keys
- [ ] Support for webhook notifications
- [ ] Trade history tracking
- [ ] Rate limiting
- [ ] HTTPS support
- [ ] Multi-trade queue
- [ ] Trade verification checks
- [ ] Automatic retry on failure

## Support

For plugin-specific issues:
1. Check RuneLite console for errors
2. Enable debug logging
3. Check plugin configuration
4. Review HTTP server logs

## References

- [RuneLite Plugin Hub](https://github.com/runelite/plugin-hub)
- [RuneLite API Documentation](https://static.runelite.net/api/runelite-api/)
- [Creating RuneLite Plugins](https://github.com/runelite/runelite/wiki/Creating-Plugins)
