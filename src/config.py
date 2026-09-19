import functools
import logging
import netrc
import os
import sys
import time
from configparser import ConfigParser
from pathlib import Path
from plexapi.server import PlexServer

logr = logging.getLogger( __name__ )


@functools.cache
def config_path() -> Path:
    logr.debug( f"inside {sys._getframe().f_code.co_name}" )
    env_var = 'PLEX_TOOLS_CONFIG'
    default_path = Path.home() / '.config/plex-tools/config'
    cfg_fn_path = os.getenv( env_var, default_path )
    return Path( cfg_fn_path )


@functools.cache
def config() -> ConfigParser:
    logr.debug( f"inside {sys._getframe().f_code.co_name}" )
    cfg = ConfigParser( allow_no_value=True )
    cfg.read( config_path() )
    return cfg


@functools.cache
def server_baseurl() -> str:
    logr.debug( f"inside {sys._getframe().f_code.co_name}" )
    cfg = config()
    proto = cfg['connection']['protocol']
    host = cfg['connection']['host']
    baseurl = f'{proto}://{host}'
    try:
        port = cfg['connection']['port']
    except KeyError:
        pass
    else:
        baseurl = f'{proto}://{host}:{port}'
    return baseurl


@functools.cache
def netrc_authenticators() -> netrc.netrc:
    logr.debug( f"inside {sys._getframe().f_code.co_name}" )
    server_name = config()['connection']['host']
    return netrc.netrc().authenticators( server_name )


def api_token() -> str:
    # get the "account" entry for this server
    return netrc_authenticators()[1]


@functools.cache
def server() -> PlexServer:
    logr.debug( f"inside {sys._getframe().f_code.co_name}" )
    server = PlexServer(
        baseurl=server_baseurl(),
        token=api_token()
    )
    return server


@functools.cache
def music_library() -> plexapi.library.MusicSection:
    logr.debug( f"inside {sys._getframe().f_code.co_name}" )
    section_name = config()['library']['music_library_name']
    library_section = server().library.section( section_name )
    return library_section


def lastrun_timestamp() -> float:
    return config()['runtime']['lastrun']


def mark_lastrun_timestamp():
    config().set( 'runtime', 'lastrun', str( time.time() ) )
    save()


def save_stats( stats: dict=None ) -> None:
    if not stats:
        return
    config()['stats'] = stats
    save()


def save():
    with config_path().open( mode='w' ) as fh:
        config().write( fh )
