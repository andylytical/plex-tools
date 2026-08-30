import logging
import plexapi
import config
import playlist
import mutagen
from pathlib import Path

logr = logging.getLogger( __name__ )


class Playlist_Manager:
    def __init__( self, config: config.Config ):
        self.cfg = config
        self.playlists = {}
        self.load()


    def load( self ):
        """ Get playlists from plex
        """
        for plexPL in self.cfg.music_library.playlists():
            if not plexPL.smart:
                self.playlists[ plexPL.title ] = playlist.Playlist( plexPL )
        logr.debug( f'Loaded {len(self.playlists)} playlists: {self.playlists.keys()}' )


    def get_playlists_from_file_tags( self, track: plexapi.audio.Track ) -> list:
        filepath = track.locations[0]
        codec = track.media[0].audioCodec
        # print(f"Key: {track.ratingKey}, Type: {codec}, Path: {filepath}")
        audio = mutagen.File( filepath )
        playlist_names = []
        if codec == 'mp3':
            if audio.tags:
                playlist_names = [
                    tag.desc[4:]
                    for tag in audio.tags.getall( 'TXXX' )
                    if tag.desc.startswith( 'ajl-' )
                ]
        elif codec in ( 'flac', 'vorbis', 'wmalossless', ):
            if audio.tags:
                playlist_names = [
                    k[4:]
                    for (k,v) in audio.tags
                    if k.startswith( 'ajl-' )
                ]
        else:
            raise UserWarning( f"Unsupported audio codec '{codec}' for file '{filepath}'")
        logr.debug( f"Read '{len(playlist_names)}' playlists for track '{filepath}': {playlist_names}'" )
        return playlist_names


    def update_playlists_for_track( self, track: plexapi.audio.Track) -> None:
        track_PL_names = set( self.get_playlists_from_file_tags( track ) )
        for pl_name in track_PL_names:
            self.add_track_to_playlist( pl_name, track )
        other_PL_names = set( self.playlists.keys() ) - track_PL_names
        for pl_name in other_PL_names:
            self.remove_track_from_playlist( pl_name, track )


    def add_track_to_playlist( self, PL_name: str, track: plexapi.audio.Track) -> None:
        # plexPL = self.playlists.setdefault(
        #     PL_name,
        #     playlist.Playlist.new_by_name( name=PL_name, cfg=self.cfg )
        # )
        if PL_name not in self.playlists:
            self.playlists[ PL_name ] = playlist.Playlist.new_by_name( name=PL_name, cfg=self.cfg )
        self.playlists[ PL_name ].add_track( track )


    def remove_track_from_playlist(
            self,
            PL_name: str,
            track: plexapi.audio.Track
            ) -> None:
        try:
            self.playlists[ PL_name ].remove_track( track )
        except KeyError:
            pass


    def sync( self ):
        for PL_name, PL in self.playlists.items():
            PL.sync()


if __name__ == "__main__":
    raise UserWarning( 'Nope: not a cmdline program' )
