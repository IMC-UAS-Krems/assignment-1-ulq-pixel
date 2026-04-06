"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""
from datetime import datetime, timedelta

from .playlists import Playlist, CollaborativePlaylist
from .tracks import Song
from .users import PremiumUser, FamilyMember


class StreamingPlatform:
    def __init__(self, name):
        self.name = name
        self.users = []
        self.artists = []
        self.albums = []
        self.tracks = []
        self.playlists = []
        self.sessions = []

    def add_user(self, user):
        self.users.append(user)

    def add_artist(self, artist):
        self.artists.append(artist)

    def add_album(self, album):
        self.albums.append(album)

    def add_track(self, track):
        self.tracks.append(track)

    def add_playlist(self, playlist):
        self.playlists.append(playlist)

    def add_session(self, session):
        self.sessions.append(session)
        session.user.add_session(session)

    def get_user_by_id(self, user_id):
        for user in self.users:
            if user.user_id == user_id:
                return user
        return None

    def get_track_by_id(self, track_id):
        for track in self.tracks:
            if track.track_id == track_id:
                return track
        return None

    def get_artist_by_id(self, artist_id):
        for artist in self.artists:
            if artist.artist_id == artist_id:
                return artist
        return None

    def get_album_by_id(self, album_id):
        for album in self.albums:
            if album.album_id == album_id:
                return album
        return None

    def all_users(self):
        return list(self.users)

    def all_tracks(self):
        return list(self.tracks)

    def total_listening_time_minutes(self, start, end):
        total_seconds = 0
        for session in self.sessions:
            if start <= session.timestamp <= end:
                total_seconds += session.duration_listened_seconds
        return total_seconds / 60

    def avg_unique_tracks_per_premium_user(self, days=30):
        premium_users = [user for user in self.users if isinstance(user, PremiumUser)]
        if not premium_users:
            return 0.0

        end = datetime.now()
        start = end - timedelta(days=days)
        total_unique_tracks = 0

        for user in premium_users:
            unique_track_ids = set()
            for session in user.sessions:
                if start <= session.timestamp <= end:
                    unique_track_ids.add(session.track.track_id)
            total_unique_tracks += len(unique_track_ids)

        return total_unique_tracks / len(premium_users)

    def track_with_most_distinct_listeners(self):
        if not self.sessions:
            return None

        track_listeners = {}
        for session in self.sessions:
            track = session.track
            user = session.user
            if track not in track_listeners:
                track_listeners[track] = set()
            track_listeners[track].add(user.user_id)

        best_track = None
        max_listeners = -1
        for track, listeners in track_listeners.items():
            if len(listeners) > max_listeners:
                max_listeners = len(listeners)
                best_track = track

        return best_track

    def avg_session_duration_by_user_type(self):
        grouped = {}

        for session in self.sessions:
            type_name = session.user.__class__.__name__
            if type_name not in grouped:
                grouped[type_name] = []
            grouped[type_name].append(session.duration_listened_seconds)

        result = []
        for type_name, durations in grouped.items():
            average = sum(durations) / len(durations)
            result.append((type_name, average))

        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def total_listening_time_underage_sub_users_minutes(self, age_threshold=18):
        total_seconds = 0

        for session in self.sessions:
            user = session.user
            if isinstance(user, FamilyMember) and user.age < age_threshold:
                total_seconds += session.duration_listened_seconds

        return total_seconds / 60

    def top_artists_by_listening_time(self, n=5):
        artist_minutes = {}

        for session in self.sessions:
            track = session.track
            if isinstance(track, Song):
                artist = track.artist
                minutes = session.duration_listened_seconds / 60
                if artist not in artist_minutes:
                    artist_minutes[artist] = 0
                artist_minutes[artist] += minutes

        ranked = list(artist_minutes.items())
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:n]

    def user_top_genre(self, user_id):
        user = self.get_user_by_id(user_id)
        if user is None or not user.sessions:
            return None

        genre_times = {}
        total_seconds = 0

        for session in user.sessions:
            genre = session.track.genre
            seconds = session.duration_listened_seconds
            if genre not in genre_times:
                genre_times[genre] = 0
            genre_times[genre] += seconds
            total_seconds += seconds

        if total_seconds == 0:
            return None

        top_genre = None
        top_seconds = -1
        for genre, seconds in genre_times.items():
            if seconds > top_seconds:
                top_seconds = seconds
                top_genre = genre

        percentage = (top_seconds / total_seconds) * 100
        return (top_genre, percentage)

    def collaborative_playlists_with_many_artists(self, threshold=3):
        result = []

        for playlist in self.playlists:
            if isinstance(playlist, CollaborativePlaylist):
                artist_ids = set()
                for track in playlist.tracks:
                    if isinstance(track, Song):
                        artist_ids.add(track.artist.artist_id)
                if len(artist_ids) > threshold:
                    result.append(playlist)

        return result

    def avg_tracks_per_playlist_type(self):
        normal_playlists = [p for p in self.playlists if type(p) is Playlist]
        collaborative_playlists = [p for p in self.playlists if isinstance(p, CollaborativePlaylist)]

        playlist_avg = (
            sum(len(p.tracks) for p in normal_playlists) / len(normal_playlists)
            if normal_playlists else 0.0
        )

        collaborative_avg = (
            sum(len(p.tracks) for p in collaborative_playlists) / len(collaborative_playlists)
            if collaborative_playlists else 0.0
        )

        return {
            "Playlist": playlist_avg,
            "CollaborativePlaylist": collaborative_avg,
        }

    def users_who_completed_albums(self):
        result = []

        for user in self.users:
            listened_track_ids = {session.track.track_id for session in user.sessions}
            completed_album_titles = []

            for album in self.albums:
                if not album.tracks:
                    continue

                album_track_ids = {track.track_id for track in album.tracks}
                if album_track_ids.issubset(listened_track_ids):
                    completed_album_titles.append(album.title)

            if completed_album_titles:
                result.append((user, completed_album_titles))

        return result