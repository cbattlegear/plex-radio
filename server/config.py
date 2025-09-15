import yaml

class Config:
    def __init__(self, config_file='config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found, using defaults")
            return self.get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration if file doesn't exist"""
        return {
            'channels': [
                {'name': 'Maisie Radio', 'playlist': 'Maisie Power House', 'playback': 'shuffle'}
            ]
        }

    def get_plex_config(self):
        """Get Plex server configuration from config"""
        return self.config.get('plex', {})

    def get_channels(self):
        """Get list of channels from config"""
        return self.config.get('channels', [])
    
    def get_playlist_for_channel(self, channel_name):
        """Get playlist name for a specific channel"""
        for channel in self.get_channels():
            if channel['name'] == channel_name:
                return channel['playlist']
        return None

    def get_playback_mode_for_channel(self, channel_name):
        """Get playback mode for a specific channel (shuffle or sequential)"""
        for channel in self.get_channels():
            if channel['name'] == channel_name:
                playback = channel.get('playback', 'shuffle')  # Default to shuffle
                return self.validate_playback_mode(playback)
        return 'shuffle'  # Default fallback

    def validate_playback_mode(self, playback_mode):
        """Validate and normalize playback mode"""
        if playback_mode is None:
            return 'shuffle'
        
        # Convert to lowercase and validate
        playback_mode = str(playback_mode).lower().strip()
        valid_modes = ['shuffle', 'sequential']
        
        if playback_mode in valid_modes:
            return playback_mode
        else:
            print(f"Warning: Invalid playback mode '{playback_mode}'. Using default 'shuffle'. Valid options: {valid_modes}")
            return 'shuffle'

    def validate_all_channels(self):
        """Validate all channels and their playback modes"""
        channels = self.get_channels()
        validated_channels = []
        
        for channel in channels:
            # Validate required fields
            if 'name' not in channel or 'playlist' not in channel:
                print(f"Error: Channel missing required fields (name/playlist): {channel}")
                continue
            
            # Validate and normalize playback mode
            original_playback = channel.get('playback')
            validated_playback = self.validate_playback_mode(original_playback)
            
            # Create validated channel
            validated_channel = channel.copy()
            validated_channel['playback'] = validated_playback
            validated_channels.append(validated_channel)
            
            # Log if playback mode was corrected or defaulted
            if original_playback is None:
                print(f"Channel '{channel['name']}': Using default playback mode 'shuffle'")
            elif original_playback != validated_playback:
                print(f"Channel '{channel['name']}': Corrected playback mode from '{original_playback}' to '{validated_playback}'")
        
        return validated_channels

# Usage example
if __name__ == "__main__":
    config = Config('example.yaml')
    
    # Get all channels
    channels = config.get_channels()
    print("Available channels:")
    for channel in channels:
        playback_mode = channel.get('playback', 'shuffle')
        print(f"  - {channel['name']}: {channel['playlist']} (playback: {playback_mode})")
    
    # Get specific playlist and playback mode
    playlist = config.get_playlist_for_channel("Maisie Radio")
    playback_mode = config.get_playback_mode_for_channel("Maisie Radio")
    print(f"\nPlaylist for Maisie Radio: {playlist}")
    print(f"Playback mode for Maisie Radio: {playback_mode}")