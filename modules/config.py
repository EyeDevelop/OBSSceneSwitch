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
    keys_needed = {
        "start_scene": [str, None],
        "unknown_app_scene": [str, None],
        "delay_time": [int],
        "window_class": [dict],
        "window_name": [dict],
        "desktop_name": [dict],
    }

    for key in conf.keys():
        if type(conf[key]) not in keys_needed[key]:
            LOGGER.warning("Root key '{}' is not of type: {}".format(
                key,
                keys_needed[key]
            ))

        if key in keys_needed.keys():
            del keys_needed[key]
        else:
            LOGGER.warning("Ignoring unknown root key {}".format(key))

    if len(keys_needed.keys()) > 0:
        LOGGER.warning(
            "You are missing the following main-level keys in your screens.json:\n\t\t" + ", ".join(keys_needed))

    # Test if all the window classes / names have the correct values and exist.
    scan_type = {
        "window_class": [dict],
        "window_name": [dict],
        "desktop_name": [dict]
    }

    for sub_type in scan_type.keys():
        for key in conf[sub_type].keys():
            sub_keys = {
                "strict_match": [bool],
                "scene": [str, None]
            }

            for sub_key in conf[sub_type][key].keys():
                sub_val = conf[sub_type][key][sub_key]
                if type(sub_val) not in sub_keys[sub_key]:
                    LOGGER.warning("Sub key {} -> {} -> {} is not of type: {}".format(
                        sub_type,
                        key,
                        sub_key,
                        sub_keys[sub_key]
                    ))

                if sub_key in sub_keys.keys():
                    del sub_keys[sub_key]
                else:
                    LOGGER.warning("Unknown sub key {} found in {} -> {}".format(sub_key, key, sub_type))

            if len(sub_keys.keys()) > 0:
                LOGGER.warning("Key {} -> {} is missing the following required sub keys:\n\t\t{}".format(sub_type, key,
                                                                                                         ", ".join(
                                                                                                             sub_keys.keys())))


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
    },
    "desktop_name": {
    }
}"""

    with open(os.path.join(SCRIPT_LOCATION, "screens.json"), "wt") as fp:
        fp.write(base_config)


def read_config_windows() -> Tuple[dict, dict, dict]:
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
    strict = {}
    rel = {}

    # Get all the data and populate the strict and rel dictionaries.
    for root_key in ["window_class", "window_name", "desktop_name"]:
        strict[root_key] = []
        rel[root_key] = []

        for wm_class in conf[root_key].keys():
            if conf[root_key][wm_class]["strict_match"]:
                strict[root_key].append(wm_class)
            else:
                rel[root_key].append(wm_class)

    return strict, rel, conf
