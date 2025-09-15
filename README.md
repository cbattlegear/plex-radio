# Plex Radio API

A REST API that simulates radio channels by providing information about the currently playing song from Plex playlists based on the time of day. Each channel generates a daily shuffled playlist and calculates which song should be playing at any given moment.

## Features

- **Time-based playback simulation**: Calculates what song should be playing based on current time
- **Multiple radio channels**: Support for multiple configured channels/playlists
- **Flexible playback modes**: Choose between sequential or shuffle playback for each channel
- **Daily playlist generation**: Creates 24-hour playlists for each channel with configurable playback order
- **Current and next song info**: Returns both current and upcoming track details
- **YAML configuration**: Easy configuration of Plex server and channels
- **Direct media links**: Provides direct URLs to media files for playback

## API Endpoints

### GET /current-song
Returns the current song information from the default channel (channel 0).

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "title": "Song Title",
    "start_time": 45,
    "media_link": "http://192.168.0.1:32400/library/parts/12345/file.mp3",
    "duration": 180.5,
    "artist": "Artist Name",
    "album": "Album Name",
    "next_song": {
      "title": "Next Song Title",
      "start_time": 0,
      "media_link": "http://192.168.0.1:32400/library/parts/12346/file.mp3",
      "duration": 210.3,
      "artist": "Next Artist",
      "album": "Next Album"
    }
  },
  "timestamp": "2025-08-25T10:30:00.123456"
}
```

### GET /current-song/\<channel_number>
Returns the current song information from a specific channel by number (0-based index).

**Parameters:**
- `channel_number`: Integer representing the channel index (0, 1, 2, etc.)

**Response Example:**
```json
{
  "status": "success",
  "data": {
    "title": "Jazz Song Title",
    "start_time": 23,
    "media_link": "http://192.168.0.1:32400/library/parts/12347/file.mp3",
    "duration": 245.7,
    "artist": "Jazz Artist",
    "album": "Jazz Album",
    "next_song": {
      "title": "Next Jazz Song",
      "start_time": 0,
      "media_link": "http://192.168.0.1:32400/library/parts/12348/file.mp3",
      "duration": 198.2,
      "artist": "Next Jazz Artist",
      "album": "Next Jazz Album"
    }
  },
  "timestamp": "2025-08-25T10:30:00.123456",
  "channel": {
    "name": "Jazz Radio",
    "playlist": "Jazz Radio",
    "playback": "shuffle"
  }
}
```

### GET /channels
Lists all configured radio channels.

**Response Example:**
```json
{
  "status": "success",
  "data": [
    {
      "name": "Jazz Radio", 
      "playlist": "Jazz Radio",
      "playback": "shuffle"
    },
    {
      "name": "Rock Radio",
      "playlist": "Rock Radio",
      "playback": "sequential"
    }
  ],
  "count": 2
}
```

### GET /health
Health check endpoint to verify API and Plex server connectivity.

**Response Example:**
```json
{
  "status": "healthy",
  "plex_server": "http://192.168.0.1:32400",
  "timestamp": "2025-08-25T10:30:00.123456"
}
```

## Installation

1. Clone or download the project
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # or on Windows
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your setup:
   ```bash
   # Copy the example configuration
   cp server/configuration/example_plex_radio_config.yaml server/configuration/plex_radio_config.yaml
   
   # Edit the configuration file
   nano server/configuration/plex_radio_config.yaml
   ```

   Update the configuration with your Plex server details:
   ```yaml
   plex:
     host: "http://your-plex-server-ip:32400"
     token: "your-plex-token"

   channels:
     - name: "Jazz Radio"
       playlist: "Your Jazz Playlist Name"
       playback: "shuffle"  # Optional: "shuffle" (default) or "sequential"
     - name: "Rock Radio"
       playlist: "Your Rock Playlist Name"
       playback: "sequential"  # Play songs in playlist order
   ```

## Configuration

The API uses a YAML configuration file located at `server/configuration/plex_radio_config.yaml`.

### Getting Your Plex Token
To find your Plex authentication token:
1. Log into your Plex account at https://app.plex.tv
2. Open browser developer tools (F12)
3. Go to any Plex page and look for the `X-Plex-Token` in the network requests
4. Alternatively, use the PlexAPI documentation for token generation

### Configuration Structure
```yaml
plex:
  host: "http://192.168.1.100:32400"  # Your Plex server URL
  token: "your-plex-token-here"       # Your Plex authentication token

channels:
  - name: "Jazz Radio"                # Display name for the channel
    playlist: "Jazz Favorites"        # Exact name of your Plex playlist
    playback: "shuffle"               # Optional: "shuffle" (default) or "sequential"
  - name: "Rock Radio"
    playlist: "Rock Classics"
    playback: "sequential"            # Play songs in playlist order
  - name: "Pop Radio"                 # playback field is optional
    playlist: "Pop Hits"              # Defaults to "shuffle" if playback not specified
```

### Playback Modes
- **shuffle** (default): Songs are shuffled daily, creating a random order each day
- **sequential**: Songs play in their original playlist order, allowing you to listen through albums or curated sequences

## Usage

### Option 1: Direct Python Execution

1. Navigate to the server directory and start the API:
   ```bash
   cd server
   python plex_radio_api.py
   ```

2. The API will be available at `http://localhost:5000`

### Option 2: Docker (Recommended)

1. Make sure you have your configuration file set up:
   ```bash
   cp server/configuration/example_plex_radio_config.yaml server/configuration/plex_radio_config.yaml
   # Edit the configuration with your Plex details
   nano server/configuration/plex_radio_config.yaml
   ```

2. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Or build and run with Docker directly:
   ```bash
   # Build the image
   docker build -t plex-radio-api .
   
   # Run the container
   docker run -d \
     --name plex-radio-api \
     -p 5000:5000 \
     -v $(pwd)/server/configuration:/app/server/configuration:ro \
     plex-radio-api
   ```

4. Check the logs:
   ```bash
   docker-compose logs -f  # For docker-compose
   docker logs -f plex-radio-api  # For direct docker run
   ```

5. Stop the service:
   ```bash
   docker-compose down  # For docker-compose
   docker stop plex-radio-api && docker rm plex-radio-api  # For direct docker run
   ```

### Testing the API

Once running (either method), test the endpoints:
```bash
# Get current song from default channel (channel 0)
curl http://localhost:5000/current-song

# Get current song from specific channel (by number)
curl http://localhost:5000/current-song/1

# List all configured channels
curl http://localhost:5000/channels

# Health check
curl http://localhost:5000/health
```

## How It Works

The API simulates radio stations by:

1. **Daily Playlist Generation**: At startup, it creates 24-hour playlists for each configured channel, either shuffled or in sequential order based on the `playback` setting
2. **Time-based Calculation**: Uses current time of day (seconds since midnight) to determine position in the playlist
3. **Song Position**: Calculates exactly where within a song playback should start
4. **Seamless Playback**: Provides both current song and next song information for gapless transitions

### Example Workflow:
- At 10:30 AM, if the playlist has been playing since midnight
- Calculate total seconds since midnight: 37,800 seconds
- Find which song should be playing at that time offset
- Return the song with exact start position within that track

## Example Usage with Media Players

### With ffplay
```bash
# Get current song info
response=$(curl -s http://localhost:5000/current-song)

# Extract media link and start time (requires jq)
media_link=$(echo $response | jq -r '.data.media_link')
start_time=$(echo $response | jq -r '.data.start_time')

# Play with ffplay
ffplay -ss $start_time -i "$media_link" -nodisp -autoexit
```

### With VLC (command line)
```bash
vlc --start-time=$start_time "$media_link" --intf dummy --play-and-exit
```

## Project Structure

```
plex-radio/
├── .venv/                               # Virtual environment
├── server/                              # Main application directory
│   ├── plex_radio_api.py               # Main API server
│   ├── config.py                       # Configuration loader
│   ├── daily_playlist.py               # Daily playlist generator
│   └── configuration/                  # Configuration files
│       ├── example_plex_radio_config.yaml  # Example configuration
│       └── plex_radio_config.yaml          # Your actual configuration
├── requirements.txt                     # Python dependencies
├── Dockerfile                          # Docker container definition
├── docker-compose.yml                 # Docker Compose configuration
├── .dockerignore                       # Docker ignore rules
├── README.md                           # This file
└── .gitignore                          # Git ignore rules
```

## Docker Configuration

The project includes Docker support for easy deployment:

### Dockerfile Features
- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for container monitoring
- **Production-ready** Flask configuration
- **Volume mounting** for configuration files

### Docker Compose Features
- **Automatic restart** on failure
- **Health monitoring** with built-in checks
- **Volume mapping** for easy configuration updates
- **Network isolation** for security

### Environment Variables
You can override configuration using environment variables:
- `FLASK_ENV`: Set to `production` for production deployment
- `PYTHONUNBUFFERED`: Ensures Python output is not buffered

## Error Handling

The API includes comprehensive error handling for:
- **Plex server connectivity issues**
- **Missing or invalid playlists**
- **Invalid channel numbers**
- **YAML configuration errors**
- **Network timeouts**
- **Invalid requests**

## Dependencies

- **Flask**: Web framework for the REST API
- **PlexAPI**: Python library for Plex server communication  
- **PyYAML**: YAML configuration file parsing
- **Python 3.7+**: Required Python version
- **Docker** (optional): For containerized deployment

## Notes

- The configuration file `plex_radio_config.yaml` is gitignored for security
- Use the `example_plex_radio_config.yaml` as a template
- Each channel generates a new playlist daily at startup (shuffled or sequential based on configuration)
- Start times are calculated as seconds into the current song
- The API runs in debug mode by default (disable for production)
- Docker deployment automatically runs in production mode
- Sequential playback preserves original playlist order, perfect for concept albums or DJ mixes
- Shuffle mode provides variety while maintaining the radio experience
