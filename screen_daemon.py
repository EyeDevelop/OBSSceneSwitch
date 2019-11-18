#!/usr/bin/env python3

import subprocess
import re
import json
import os
import time
from typing import Union, Tuple, List

SCRIPT_LOCATION = os.path.abspath(os.path.dirname(__file__))


def generate_config():
    base_config = """{
    "start_scene": "Coding",
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
    "window_name": {}
}"""

    with open(os.path.join(SCRIPT_LOCATION, "screens.json"), "wt") as fp:
        fp.write(base_config)


def get_active_window_info() -> Union[None, Tuple[List[str], str]]:
    # Get the active window from the window manager.
    p = subprocess.Popen(["xprop", "-root", "_NET_ACTIVE_WINDOW"], stdout=subprocess.PIPE)
    root_info, _ = p.communicate()
    root_info = root_info.decode("utf-8")

    # Check if it can be extracted, otherwise return nothing.
    m = re.search(r'^_NET_ACTIVE_WINDOW.* ([\w]+)$', root_info)
    if not m:
        return None

    # Get the active window id.
    window_id = m.group(1)

    # Get information about the active window.
    p = subprocess.Popen(["xprop", "-id", window_id, "WM_CLASS", "WM_NAME"], stdout=subprocess.PIPE)
    active_window_info, _ = p.communicate()
    active_window_info = active_window_info.decode("utf-8")

    # Extract the useful info bits, the window title name and the window class.
    m = re.search(r'= (.*)\n.* = (.*)', active_window_info)
    if not m:
        return None

    # Split classes on comma and return a tuple of classes
    # and window title.
    return m.group(1).replace('"', '').split(", "), m.group(2)


def read_config() -> Tuple[List[str], List[str], List[str], List[str], dict]:
    # Get the config contents.
    conf = json.load(open(os.path.join(SCRIPT_LOCATION, "screens.json"), 'r'))

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


def check_new_scene() -> Union[None, Tuple[str, str]]:
    data = get_active_window_info()
    if not data:
        return None

    window_classes, window_name = data
    strict_classes, strict_name, rel_classes, rel_name, conf = read_config()

    # First do strict class matching.
    for wm_class in window_classes:
        for c_class in strict_classes:
            if wm_class == c_class:
                return conf["window_class"][wm_class]["scene"], wm_class

    # Now do relative class matching.
    for wm_class in window_classes:
        for c_class in rel_classes:
            if c_class.lower() in wm_class.lower():
                return conf["window_class"][c_class]["scene"], wm_class

    # Do strict name matching.
    for c_name in strict_name:
        if window_name == c_name:
            return conf["window_name"][c_name]["scene"], window_name

    # Do relative name matching.
    for c_name in rel_name:
        if c_name.lower() in window_name.lower():
            return conf["window_name"][c_name]["scene"], window_name

    return None


def write_scene_to_file(scene: str):
    with open(os.path.join(SCRIPT_LOCATION, "scene.txt"), "wt") as fp:
        fp.write(scene)


def main():
    if not os.path.isfile(os.path.join(SCRIPT_LOCATION, "screens.json")):
        generate_config()
        print("\nConfig not found. New one has been generated. Please look and modify the config before running again.")
        exit(0)

    init_conf = json.load(open(os.path.join(SCRIPT_LOCATION, "screens.json")))

    # Set the scene to the beginning scene.
    current_scene = init_conf["start_scene"]
    write_scene_to_file(current_scene)

    print("Setup is done. Starting daemon...")
    while True:
        data = check_new_scene()
        if not data:
            continue

        new_scene, active_app = data
        if new_scene == current_scene or not new_scene:
            continue

        print("Known active app changed to {}. Changing scene to {}.".format(
            active_app,
            new_scene
        ))

        write_scene_to_file(new_scene)
        current_scene = new_scene

        time.sleep(init_conf["delay_time"] / 1000)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting daemon...")
