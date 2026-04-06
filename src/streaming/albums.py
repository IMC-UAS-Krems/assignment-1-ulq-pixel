"""
albums.py
---------
Implement the Album class for collections of AlbumTrack objects.

Classes to implement:
  - Album
"""
class Album:
    def __init__(self, album_id, title, artist, release_year):
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_year = release_year
        self.tracks = []
#
    def add_track(self, track):
        self.tracks.append(track)
        self.tracks.sort(key=lambda t: t.track_number)
        track.album = self
#
    def track_ids(self):
        return {track.track_id for track in self.tracks}
#
    def duration_seconds(self):
        return sum(track.duration_seconds for track in self.tracks)