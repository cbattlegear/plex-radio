from plexapi.server import PlexServer
import datetime
import random

class DailyPlaylist:
    def __init__(self, plex, channel_playlist_name, playback_mode='shuffle'):
        self.plex = plex
        self.channel_playlist_name = channel_playlist_name
        self.playback_mode = playback_mode  # 'shuffle' or 'sequential'
        self.current_playlist = None
        self.creation_time = datetime.datetime.now()
        self.playlist_items = None
        self.refresh_if_needed()

    def generate_playlist(self):
        """Generate a playlist that is limited to 24 hours long, with optional shuffling"""
        # Create a copy of the playlist to avoid modifying the original
        playlist_copy = self.current_playlist.copy()
        
        # Apply shuffling based on playback mode
        if self.playback_mode == 'shuffle':
            random.shuffle(playlist_copy)
        # For sequential mode, we keep the original order

        limited_playlist = []
        # Limit the playlist to 24 hours
        for item in playlist_copy:
            total_duration = sum(item.duration for item in limited_playlist)
            if total_duration < 24 * 60 * 60 * 1000:  # 24 hours in milliseconds
                limited_playlist.append(item)

        return limited_playlist
    
    def is_expired(self):
        """Check if this playlist is more than 24 hours old"""
        now = datetime.datetime.now()
        time_difference = now - self.creation_time
        return time_difference > datetime.timedelta(hours=24)
    
    def get_age_hours(self):
        """Get the age of this playlist in hours"""
        now = datetime.datetime.now()
        time_difference = now - self.creation_time
        return time_difference.total_seconds() / 3600
    
    def refresh_if_needed(self):
        if self.is_expired() or self.playlist_items is None:
            self.current_playlist = self.plex.playlist(self.channel_playlist_name).items()
            self.playlist_items = self.generate_playlist()
            self.creation_time = datetime.datetime.now()
