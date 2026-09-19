import plexapi
import config
import logging

logr = logging.getLogger( __name__ )

class Playlist:
    def __init__(
            self,
            playlist: plexpai.Playlist = None,
            name: str = None,
            ) -> Playlist:
        self.playlist = playlist
        self.name = name
        self.tracks = []
        if self.playlist:
            self.tracks = playlist.items()
            self.name = self.playlist.title
        self.pending_additions = []
        self.pending_deletions = []


    @classmethod
    def new_by_name( cls, name: str ) -> Playlist:
        ''' Workaround for Plex's inability to create an empty playlist
        '''
        logr.debug( f"New playlist '{name}'" )
        return cls( name=name )


    def add_track( self, track: plexapi.audio.Track ) -> None:
        if track not in self.tracks:
            logr.debug( f"queing add track '{track}' to playlist '{self.name}'" )
            self.pending_additions.append( track )


    def remove_track( self, track: plexapi.audio.Track ) -> None:
        if track in self.tracks:
            logr.debug( f"queing remove track '{track}' from playlist '{self.name}'" )
            self.pending_deletions.append( track )


    def sync( self ):
        ''' Create the actual Plex playlist
            Or update with additions and deletions
        '''
        if not self.playlist:
            if self.pending_additions:
                logr.debug( f"Create new playlist '{self.name}' with tracks '{self.pending_additions}'" )
                self.playlist = config.music_library().createPlaylist(
                    title=self.name,
                    items=self.pending_additions
                )
        else:
            # add anything that's not already in the playlist
            if self.pending_additions:
                logr.debug( f"Add to playlist '{self.name}': '{self.pending_additions}'" )
                self.playlist.addItems( self.pending_additions )
            # attempt to delete tracks
            if self.pending_deletions:
                logr.debug( f"Remove from playlist '{self.name}': '{self.pending_deletions}'" )
                self.playlist.removeItems( self.pending_deletions )
