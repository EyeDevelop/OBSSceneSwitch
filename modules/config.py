import json
import logging
import os
import time
from typing import Tuple, List

from modules.logger import get_logger

SCRIPT_LOCATION = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
LOGGER = get_logger(logging.INFO, __name__)
CONFIG_CHECKED = False


def check_config(conf):
    """
    Checks the config file for errors and logs them if found.

    :param conf: The config dictionary.
    :return: Nothing.
    """

    # Test if all keys are in the file.
    keys_needed = ["start_scene", "unknown_app_scene", "delay_time", "window_class", "window_name"]
    for key in conf.keys():
        if key in keys_needed:
            keys_needed.remove(key)
        else:
            LOGGER.warning("Ignoring unknown root key {}".format(key))

        if key == "start_scene" and not isinstance(conf[key], str):
            LOGGER.warning("The root key 'start_scene' has a wrong type. It needs to be a string.")

        if key == "unknown_app_scene" and (not isinstance(conf[key], str) and conf[key]):
            LOGGER.warning("The root key 'unknown_app_scene' has a wrong type. Needs to be a string or null.")

        if key == "delay_time" and not isinstance(conf[key], int):
            LOGGER.warning("The root key 'delay_time' has a wrong type. It needs to be a number.")

        if key == "window_class" and not isinstance(conf[key], dict):
            LOGGER.critical("The root key 'window_class' is not a dictionary. This needs to be fixed.")
            exit(1)

        if key == "window_name" and not isinstance(conf[key], dict):
            LOGGER.critical("The root key 'window_name' is not a dictionary. This needs to be fixed.")
            exit(1)

    if len(keys_needed) > 0:
        LOGGER.warning(
            "You are missing the following main-level keys in your screens.json:\n\t\t" + ", ".join(keys_needed))

    # Test if all the window classes / names have the correct values and exist.
    for sub_type in ["window_class", "window_name"]:
        for key in conf[sub_type].keys():
            sub_keys_needed = ["strict_match", "scene"]
            for sub_key in conf[sub_type][key].keys():
                if sub_key in sub_keys_needed:
                    sub_keys_needed.remove(sub_key)
                else:
                    LOGGER.warning("Unknown sub key {} found in {} -> {}".format(sub_key, key, sub_type))

                sub_val = conf[sub_type][key][sub_key]
                if sub_key == "strict_match" and not isinstance(sub_val, bool):
                    LOGGER.warning(
                        "Sub key {} -> {} -> {} is of wrong type. Needs to be either 'true' or 'false'".format(sub_type,
                                                                                                               key,
                                                                                                               sub_key))

                if sub_key == "scene" and (not isinstance(sub_val, str) and sub_val):
                    LOGGER.warning(
                        "Sub key {} -> {} -> {} is of wrong type. Needs to be a string or null".format(sub_type, key,
                                                                                                       sub_key))

            if len(sub_keys_needed) > 0:
                LOGGER.warning("Key {} -> {} is missing the following required sub keys:\n\t\t{}".format(sub_type, key,
                                                                                                         ", ".join(
                                                                                                             sub_keys_needed)))


def parse_config() -> dict:
    """
    Checks the config file. Then returns the parsed JSON document as dictionary object.

    :return: Nothing.
    """
    global CONFIG_CHECKED

    # Open the config file.
    try:
        conf = json.load(open(os.path.join(SCRIPT_LOCATION, "screens.json"), "r"))
    except json.JSONDecodeError:
        LOGGER.critical("Cannot read config file. Trying again in 5 seconds...")
        time.sleep(5)
        return parse_config()

    # Check the config file for errors.
    if not CONFIG_CHECKED:
        CONFIG_CHECKED = True
        check_config(conf)

    # Return the config file.
    return conf


def generate_config():
    """
    Generates a base config and writes it to screens.json.
    Useful when no config is found.

    :return: Nothing.
    """

    base_config = """{
    "start_scene": "Coding",
    "unknown_app_scene": "Privacy",
    "delay_time": 300,
    "window_class": {
        "google-chrome": {
            "strict_match": true,
            "scene": "Research"
        },
        "jetbrains": {
            "strict_match": false,
            "scene": "Coding"
        }
    },
    "window_name": {
        "whatsapp": {
            "strict_match": false,
            "scene": "Privacy"
        }
    }
}"""

    with open(os.path.join(SCRIPT_LOCATION, "screens.json"), "wt") as fp:
        fp.write(base_config)


def read_config_windows() -> Tuple[List[str], List[str], List[str], List[str], dict]:
    """
    Reads all the window class and name directives from the config.
    Returns them as list.

    Running this in the main loop means that the config file is hot-swappable.
    Add as you please, even when the program is running.

    :return: A tuple of the strict classes, strict names, non-strict classes and non-strict names. The final
    element in the tuple is the rest of the config dictionary.
    """

    # Get the config contents.
    conf = parse_config()

    # Split the strict classes from the not strict classes.
    strict_classes = []
    rel_classes = []
    for wm_class in conf["window_class"].keys():
        if conf["window_class"][wm_class]["strict_match"]:
            strict_classes.append(wm_class)
        else:
            rel_classes.append(wm_class)

    # Do the same for the window name.
    strict_name = []
    rel_name = []
    for wm_name in conf["window_name"].keys():
        if conf["window_name"][wm_name]["strict_match"]:
            strict_name.append(wm_name)
        else:
            rel_name.append(wm_name)

    return strict_classes, strict_name, rel_classes, rel_name, conf
