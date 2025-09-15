from flask import Flask, jsonify
from plexapi.server import PlexServer
import datetime
import config
import daily_playlist
from unidecode import unidecode
import os

app = Flask(__name__)

# Use the correct config file path
config_path = os.path.join(os.path.dirname(__file__), 'configuration', 'plex_radio_config.yaml')
current_config = config.Config(config_path)

# Plex server configuration
plex_config = current_config.get_plex_config()
BASEURL = plex_config.get('host', 'http://localhost:32400')
TOKEN = plex_config.get('token', 'YOUR_DEFAULT_TOKEN')
plex = PlexServer(BASEURL, TOKEN)

channel_playlists = []

def generate_daily_playlists():
    """
    Generate daily playlists for each channel based on the current playlist.
    """
    channel_playlists.clear()  # Clear existing playlists

    for channel in current_config.validate_all_channels():
        playback_mode = channel['playback']  # Already validated
        daily_playlist_instance = daily_playlist.DailyPlaylist(
            plex, 
            channel['playlist'], 
            playback_mode
        )
        channel_playlists.append(daily_playlist_instance)

def initialize_app():
    """Initialize the application - called when the module is imported"""
    print("Starting Plex Radio API...")
    print("Available endpoints:")
    print("  GET /current-song - Get current song from default playlist")
    print("  GET /current-song/<channel_number> - Get current song from specific channel")
    print("  GET /channels - List all available channels")
    print("  GET /health - Health check")

    print("Generating daily playlists...")
    generate_daily_playlists()
    print("Plex Radio API initialized successfully!")

# Initialize when the module is imported (for Gunicorn)
initialize_app()

def calculate_current_song_info(channel_number=0):
    """
    Calculate the current song that should be playing based on time of day
    and return its information including title, start time, and media link
    """
    
    # Added extra process to refresh the playlist if needed, this can cause initial slow load though
    channel_playlists[channel_number].refresh_if_needed()
    
    try:
        # Find the specified playlist
        target_playlist = channel_playlists[channel_number] if channel_number < len(channel_playlists) else None
        
        if not target_playlist:
            return None, f"Channel '{channel_number}' not found"

        # Calculate playlist duration in seconds
        playlist_duration_in_seconds = sum(item.duration for item in target_playlist.playlist_items) / 1000

        # Calculate current time in seconds since midnight
        now = datetime.datetime.now()
        seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
        
        # Calculate where we should be in the playlist
        playlist_start_time = seconds_since_midnight % playlist_duration_in_seconds
        
        # Find the current item and calculate start time within that item
        cumulative_time = 0
        for index, item in enumerate(target_playlist.playlist_items):
            item_duration = item.duration / 1000
            
            if playlist_start_time < cumulative_time + item_duration:
                # This is the current item
                start_time_in_item = playlist_start_time - cumulative_time
                
                song_info = {
                    "title": unidecode(item.title),
                    "start_time": round(start_time_in_item),
                    "media_link": f"{BASEURL}{item.media[0].parts[0].key}",
                    "duration": item_duration,
                    "artist": unidecode(getattr(item, 'grandparentTitle', 'Unknown')) if hasattr(item, 'grandparentTitle') else 'Unknown',
                    "album": unidecode(getattr(item, 'parentTitle', 'Unknown')) if hasattr(item, 'parentTitle') else 'Unknown'
                }

                next_song_index = index + 1 if index+1 < len(target_playlist.playlist_items) else 0
                
                next_item = target_playlist.playlist_items[next_song_index]

                next_song_info = {
                    "title": unidecode(next_item.title),
                    "start_time": 0,
                    "media_link": f"{BASEURL}{next_item.media[0].parts[0].key}",
                    "duration": next_item.duration/1000,
                    "artist": unidecode(getattr(next_item, 'grandparentTitle', 'Unknown')) if hasattr(next_item, 'grandparentTitle') else 'Unknown',
                    "album": unidecode(getattr(next_item, 'parentTitle', 'Unknown')) if hasattr(next_item, 'parentTitle') else 'Unknown'
                }

                song_info["next_song"] = next_song_info

                return song_info, None
            
            cumulative_time += item_duration
        
        return None, "No matching item found in playlist"
        
    except Exception as e:
        return None, f"Error: {str(e)}"

@app.route('/current-song', methods=['GET'])
def get_current_song():
    """
    GET /current-song
    Returns the current song information based on time of day
    """
    song_info, error = calculate_current_song_info()
    
    if error:
        return jsonify({"error": error}), 404
    print(song_info)
    return jsonify({
        "status": "success",
        "data": song_info,
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/current-song/<channel_number>', methods=['GET'])
def get_current_song_from_channel(channel_number):
    """
    GET /current-song/<channel_number>
    Returns the current song information from a specific channel
    """

    channels = current_config.get_channels()
    if not channels or int(channel_number) < 0 or int(channel_number) >= len(channels):
        return jsonify({"error": "Invalid channel number"}), 404

    channel = channels[int(channel_number)]
    song_info, error = calculate_current_song_info(int(channel_number))

    if error:
        return jsonify({"error": error}), 404
    
    return jsonify({
        "status": "success",
        "data": song_info,
        "timestamp": datetime.datetime.now().isoformat(),
        "channel": {
            "name": channel['name'],
            "playlist": channel['playlist'],
            "playback": channel.get('playback', 'shuffle')
        }
    })

@app.route('/channels', methods=['GET'])
def get_channels():
    """
    GET /channels
    Returns a list of available channels with their validated playback modes
    """
    try:
        # Get validated channels with proper playback modes
        channels = current_config.validate_all_channels()
        
        return jsonify({
            "status": "success",
            "data": channels,
            "count": len(channels)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    GET /health
    Simple health check endpoint
    """
    try:
        # Test Plex connection
        plex.library
        return jsonify({
            "status": "healthy",
            "plex_server": BASEURL,
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':    
    app.run(debug=True, host='0.0.0.0', port=5000)
