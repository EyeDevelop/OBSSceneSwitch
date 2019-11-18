import logging
import re
import subprocess
import sys
from typing import Union, Tuple, List

from modules.logger import get_logger

LOGGER = get_logger(logging.INFO, __name__)


def get_active_window_info_linux() -> Union[None, Tuple[List[str], str]]:
    """
    Function that uses the xprop command line utility to gather information about the active window.
    Returns None if it can't get the info.

    :return: The window classes and the window title.
    """

    # Get the active window from the window manager.
    p = subprocess.Popen(["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    root_info, _ = p.communicate()
    root_info = root_info.decode("utf-8")

    # Check if it can be extracted, otherwise return nothing.
    m = re.search(r'^_NET_ACTIVE_WINDOW.* ([\w]+)$', root_info)
    if not m:
        return None

    # Get the active window id.
    window_id = m.group(1)

    # Get information about the active window.
    p = subprocess.Popen(["xprop", "-id", window_id, "WM_CLASS", "WM_NAME"], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    active_window_info, _ = p.communicate()
    active_window_info = active_window_info.decode("utf-8")

    # Extract the useful info bits, the window title name and the window class.
    m = re.search(r'= (.*)\n.* = (.*)', active_window_info)
    if not m:
        return None

    # Split classes on comma and return a tuple of classes
    # and window title.
    return m.group(1).replace('"', '').split(", "), m.group(2)


def get_active_window_info_windows() -> Union[None, Tuple[List[str], str]]:
    """
    Function that uses the Windows API to get information about the current active screen.
    Returns None if it can't get the info.

    :return: The executable that spawned the window and the window title.
    """

    # Try to import the pywin32 library.
    try:
        from win32gui import GetWindowText, GetForegroundWindow
    except ImportError:
        LOGGER.critical("Could not import the pywin32 library. Please install it.")
        exit(1)

    # Use it to get the current window name.
    window_title = GetWindowText(GetForegroundWindow())

    # Return the process name and the active windows.
    return [""], window_title


def get_active_window_info() -> Union[None, Tuple[List[str], str]]:
    """
    Wrapper function that returns the right result for the right OS.

    :return: The right window details depending on the OS.
    """

    # Return the right result.
    if sys.platform == "linux":
        return get_active_window_info_linux()

    elif sys.platform == "win32":
        return get_active_window_info_windows()

    else:
        LOGGER.critical("This OS is not supported.")
        exit(1)
