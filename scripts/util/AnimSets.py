import os
from pathlib import Path

IS_WINDOWS = os.name == 'nt'
IS_LINUX = os.name == 'posix'



def get_game_file_path() -> Path:
    # access environment variable for the game files
    # this is detailed in the README
    GAME_FILE_PATH = os.getenv("PZ_GAME_PATH")

    # verify it is set
    if not GAME_FILE_PATH:
        raise EnvironmentError("Environment variable 'PZ_GAME_PATH' is not set. Please set it to the root directory of your Project Zomboid installation.")
    
    # verify it's a valid directory
    game_file_path = Path(GAME_FILE_PATH)
    if not game_file_path.is_dir():
        raise NotADirectoryError(f"The path specified in 'PZ_GAME_PATH' does not exist or is not a directory: {GAME_FILE_PATH}")
    
    # verify it contains the correct files
    # - on Linux it should contain the `projectzomboid.sh` file
    # - on Windows it should contain the `ProjectZomboid64.exe` file
    if IS_WINDOWS:  # Windows
        expected_file = game_file_path / "ProjectZomboid64.exe"
    elif IS_LINUX:  # Linux and others
        expected_file = game_file_path / "projectzomboid.sh"
    else:
        raise OSError("Unsupported operating system. This script only supports Windows and Linux.")

    if not expected_file.exists():
        raise FileNotFoundError(f"The specified game directory does not contain the expected file: {expected_file}. See the README for more details on setting up the environment variable correctly.")
    
    # normalize to the media folder
    if IS_LINUX:
        game_file_path = game_file_path / "projectzomboid" / "media"
    elif IS_WINDOWS:
        game_file_path = game_file_path / "media"

    if not game_file_path.is_dir():
        raise NotADirectoryError(f"The expected media directory does not exist: {game_file_path}. Please verify your game installation and the environment variable setup.")

    return game_file_path

def get_animsets_path() -> Path:
    game_file_path = get_game_file_path()
    animsets_path = game_file_path / "AnimSets"
    if not animsets_path.is_dir():
        raise NotADirectoryError(f"The expected animsets directory does not exist: {animsets_path}. Please verify your game installation and the environment variable setup.")
    return animsets_path

def get_player_animset_path() -> Path:
    animsets_path = get_animsets_path()
    player_animset_path = animsets_path / "player"
    if not player_animset_path.is_dir():
        raise NotADirectoryError(f"The expected player animsets directory does not exist: {player_animset_path}. Please verify your game installation and the environment variable setup.")
    return player_animset_path





if __name__ == "__main__":
    # test game file path
    try:
        game_file_path = get_game_file_path()
        print(f"Game file path found at: {game_file_path}")
    except Exception as e:
        print(f"Error: {e}")

    # test AnimSets directory
    try:
        animsets_path = get_animsets_path()
        print(f"AnimSets directory found at: {animsets_path}")
    except Exception as e:
        print(f"Error: {e}")

    # test player AnimSets directory
    try:        
        player_animset_path = get_player_animset_path()
        print(f"Player AnimSets directory found at: {player_animset_path}")
    except Exception as e:
        print(f"Error: {e}")