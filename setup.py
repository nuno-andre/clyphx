from platform import system
from pathlib import Path
from shutil import rmtree, copytree
import warnings


HERE = Path(__file__).parent


def find_win_path():
    '''Returns Windows Ableton Live folder.'''
    import winreg

    # also HKCU\SOFTWARE\Ableton\{...}
    reg = winreg.ConnectRegistry(None, winreg.HKEY_CLASSES_ROOT)
    value = winreg.QueryValue(reg, r'ableton\Shell\open\command')
    path, _ = value.rsplit(' ', 1)
    return Path(path).parents[1]


def find_mac_path():
    '''Returns MacOS Ableton Live folder.'''
    raise NotImplementedError


def install():
    if system() == 'Windows':
        path = find_win_path() / 'Resources'
        print(path)
    elif system() == 'Darwin':
        path = find_mac_path() / 'Contents/App-Resources'
    else:
        raise NotImplementedError

    path /= 'MIDI Remote Scripts/ClyphX'

    if path.exists():
        warnings.warn('Removing previous installation')
        # TODO: save user settings
        rmtree(path)

    copytree(HERE / 'src/clyphx', path)


# if __name__ == '__main__':
#     install()
