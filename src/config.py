import netrc
import os

from configparser import ConfigParser
from functools import cached_property
from pathlib import Path
from plexapi.server import PlexServer


class Config;
    def __init__(
            self,
            default_cfg_path,
            cfg_path_env_var
            ):
        self.default_cfg_path = default_cfg_path
        self.cfg_path_env_var = cfg_path_env_var


    @cached_property
    def config( self ) -> ConfigParser:
        cfg_fn_path = os.getenv( self.cfg_path_env_var, self.default_cfg_path )
        configfile = Path( cfg_fn_path )
        cfg = ConfigParser( allow_no_value=True )
        cfg.read( configfile )
        return cfg


    def server( self ) -> str:
        return self.config['server']['host']


    @cached_property
    def server_baseurl( self ) -> str:
        proto = self.config['server']['protocol']
        host = self.server()
        baseurl = f'{proto}://host'
        try:
            port = self.config['server']['port']
            baseurl = f'{proto}://{host}:{port}'
        except KeyError:
            pass
        return baseurl


    @cached_property
    def netrc_authenticators() -> netrc.netrc:
        return netrc.netrc().authenticators( self.server() )


    def api_token() -> str:
        return self.netrc_authenticators['account']
