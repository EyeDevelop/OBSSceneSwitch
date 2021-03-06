#!/usr/bin/env python3
import logging
import os
import time
from typing import Union, Tuple

from modules.config import read_config_windows, generate_config, parse_config
from modules.logger import get_logger
from modules.window import get_active_window_info

SCRIPT_LOCATION = os.path.abspath(os.path.dirname(__file__))
LOGGER = get_logger(logging.INFO, __name__)


def check_new_scene() -> Union[None, Tuple[str, str]]:
    """
    Determines the new scene based on the active window.
    Reads the config before parsing, so that the config is hot-swappable.

    :return:
    """

    data = get_active_window_info()
    if not data:
        return None

    window_classes, window_name, workspace_name = data
    strict, rel, conf = read_config_windows()

    # First do workspace matching.
    for c_workspace in strict["desktop_name"]:
        if workspace_name == c_workspace:
            return conf["desktop_name"][c_workspace]["scene"], workspace_name

    # Relative workspace matching.
    for c_workspace in rel["desktop_name"]:
        if c_workspace.lower() in workspace_name.lower():
            return conf["desktop_name"][c_workspace]["scene"], workspace_name

    # Then, do strict name matching.
    for c_name in strict["window_name"]:
        if window_name == c_name:
            return conf["window_name"][c_name]["scene"], window_name

    # Do relative name matching.
    for c_name in rel["window_name"]:
        if c_name.lower() in window_name.lower():
            return conf["window_name"][c_name]["scene"], window_name

    # Now do strict class matching.
    for wm_class in window_classes:
        for c_class in strict["window_class"]:
            if wm_class == c_class:
                return conf["window_class"][wm_class]["scene"], wm_class

    # Finally, relative class matching.
    for wm_class in window_classes:
        for c_class in rel["window_class"]:
            if c_class.lower() in wm_class.lower():
                return conf["window_class"][c_class]["scene"], wm_class

    return None


def write_scene_to_file(scene: str):
    """
    Writes the scene to the scene.txt file.

    :param scene: The text to write to the scene.txt file.
    :return: Nothing.
    """

    with open(os.path.join(SCRIPT_LOCATION, "scene.txt"), "wt") as fp:
        fp.write(scene)


def main():
    """
    Main function that has the actual loop.

    :return: Nothing.
    """

    if not os.path.isfile(os.path.join(SCRIPT_LOCATION, "screens.json")):
        generate_config()
        LOGGER.info(
            "Config not found. New one has been generated. Please look and modify the config before running again.")
        exit(0)

    init_conf = parse_config()

    # Set the scene to the beginning scene.
    current_scene = init_conf["start_scene"]
    current_active = None
    write_scene_to_file(current_scene)

    # Notify ready for execution.
    LOGGER.info("Setup is done. Starting daemon...")
    while True:
        # Sleep the delay time to not overuse the CPU.
        time.sleep(init_conf["delay_time"] / 1000)

        data = check_new_scene()
        if not data:
            # App is unknown. Switch to the "unknown_app" scene.
            new_scene = init_conf["unknown_app_scene"]
            if new_scene:
                current_scene = new_scene
                write_scene_to_file(current_scene)

            continue

        # Don't change the current scene if it's the same.
        new_scene, active_app = data
        if new_scene == current_scene:
            # Log once if the focus changed but the app leads to the same scene.
            if active_app != current_active:
                LOGGER.info("Focused screen changed to known definition: {}. Not changing scene as it is the same.".format(
                    active_app
                ))

                current_active = active_app

            continue

        # Known app requested a stay of the current scene.
        elif not new_scene:
            # Log it ONCE.
            if active_app != current_active:
                LOGGER.info("Focused window changed to known app: {}. Requested stay of scene.".format(
                    active_app
                ))

                current_active = active_app

            continue

        # Log the change in scene.
        LOGGER.info("Focused window changed to known app: {}. Changing scene to {}.".format(
            active_app,
            new_scene
        ))

        # Write the scene to the scene.txt
        write_scene_to_file(new_scene)
        current_scene = new_scene
        current_active = active_app


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.info("Exiting daemon...")
