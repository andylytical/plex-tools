import time
import plexapi
import config
import logging
from playlist_manager import Playlist_Manager
from pathlib import Path


def last_file_update( track: plexapi.audio.Track ) -> float:
    return Path( track.locations[0] ).stat().st_mtime


def main() -> None:
    start = time.time()

    cfg = config.Config(
        cfg_path_env_var = 'PLEX_TOOLS_CONFIG',
        default_cfg_path = Path.home() / '.config/plex-tools/config'
    )
    lastrun = float( cfg.get_lastrun_timestamp() )

    # Create playlist manager
    PLmgr = Playlist_Manager( cfg )
    # raise SystemExit( f"DEBUG : elapsed time '{elapsed}' secs" )

    limit=None
    # limit=10000
    count=0
    elapsed = time.time() - start
    # searchTracks() calls search(libtype='track') under the hood
    for track in cfg.music_library.searchTracks( maxresults=limit ):
        count += 1
        if last_file_update( track ) > lastrun:
            PLmgr.update_playlists_for_track( track )
        if (count % 100) == 0:
            elapsed = time.time() - start
            print( f">>>>> {count} files ... in {elapsed} secs")

    PLmgr.sync()

    # cfg.mark_lastrun_timestamp()


if __name__ == "__main__":
    logfmt = '%(levelname)s:%(module)s.%(funcName)s[%(lineno)d] %(message)s'
    loglvl = logging.DEBUG
    logging.basicConfig( level=loglvl, format=logfmt )
    no_debug = [
        'connectionpool',
        'exchangelib',
        'future_stdlib',
        'grab',
        'ntlm_auth',
        'requests',
        'selection',
        'urllib3',
        'weblib',
        ]
    for key in no_debug:
        logging.getLogger(key).setLevel(logging.CRITICAL)
    main()
