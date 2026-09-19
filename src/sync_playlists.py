import time
import plexapi
import config
import logging
import pprint
from playlist_manager import Playlist_Manager
from pathlib import Path

logr = logging.getLogger( __name__ )


def last_file_update( track: plexapi.audio.Track ) -> float:
    return Path( track.locations[0] ).stat().st_mtime


def main() -> None:
    lastrun = float( config.lastrun_timestamp() )
    # config.lastrun_timestamp()
    # raise SystemExit( 'forced exit' )

    # Create playlist manager
    PLmgr = Playlist_Manager()
    # raise SystemExit( f"DEBUG : elapsed time '{elapsed}' secs" )

    total_tracks=0
    tracks_changed_since_last_run=0
    start = time.time()
    limit=None
    # limit=100
    # searchTracks() calls search(libtype='track') under the hood
    for track in config.music_library().searchTracks( maxresults=limit ):
        total_tracks += 1
        if last_file_update( track ) > lastrun:
            PLmgr.update_playlists_for_track( track )
            tracks_changed_since_last_run += 1
        if (total_tracks % 100) == 0:
            elapsed = time.time() - start
            logr.info( f"{total_tracks} tracks ... in {elapsed} secs")

    PLmgr.sync()

    config.mark_lastrun_timestamp()

    stats = {
        'runtime': time.time() - start,
        'total_tracks': total_tracks,
        'tracks_changed_since_last_run': tracks_changed_since_last_run,
    }
    config.save_stats( stats=stats )
    logr.info( f"\n{pprint.pformat( stats )}" )


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
