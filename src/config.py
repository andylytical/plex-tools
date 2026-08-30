import netrc
import os
import time

from configparser import ConfigParser
from functools import cached_property
from pathlib import Path
from plexapi.server import PlexServer


class Config:
    def __init__(
            self,
            cfg_path_env_var,
            default_cfg_path
            ):
        self.cfg_path_env_var = str( cfg_path_env_var )
        self.default_cfg_path = str( default_cfg_path )
        self.configpath = None
        self.config = None
        self.load()


    def load( self ) -> ConfigParser:
        cfg_fn_path = os.getenv( self.cfg_path_env_var, self.default_cfg_path )
        self.configpath = Path( cfg_fn_path )
        print( f'configpath: {self.configpath}' )
        self.config = ConfigParser( allow_no_value=True )
        self.config.read( self.configpath )


    def get_lastrun_timestamp( self ):
        return self.config['runtime']['lastrun']


    def mark_lastrun_timestamp( self ):
        self.config.set( 'runtime', 'lastrun', time.time() )
        self.save()


    def save( self ):
        with self.configpath.open( mode='w' ) as fh:
            self.config.write( fh )


    @cached_property
    def server_baseurl( self ) -> str:
        proto = self.config['connection']['protocol']
        host = self.config['connection']['host']
        baseurl = f'{proto}://host'
        try:
            port = self.config['connection']['port']
            baseurl = f'{proto}://{host}:{port}'
        except KeyError:
            pass
        return baseurl


    @cached_property
    def netrc_authenticators( self ) -> netrc.netrc:
        server_name = self.config['connection']['host']
        return netrc.netrc().authenticators( server_name )


    @cached_property
    def api_token( self ) -> str:
        # get the "account" entry for this server
        return self.netrc_authenticators[1]


    @cached_property
    def server( self ) -> PlexServer:
        return PlexServer(
            baseurl=self.server_baseurl,
            token=self.api_token
        )


    @cached_property
    def music_library( self ) -> plexapi.library.MusicSection:
        return self.server.library.section(
            self.config['library']['music_library_name']
        )
