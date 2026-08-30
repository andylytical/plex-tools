import config
from pathlib import Path


def main() -> None:

    cfg = config.Config(
        cfg_path_env_var = 'PLEX_TOOLS_CONFIG_PATH',
        default_cfg_path = Path.home() / '.config/plex-tools/config'
    )

    for playlist in cfg.server.playlists():
        playlist.delete()
        print( f"Deleted playlist '{playlist.title}'" )


if __name__ == "__main__":
    main()
