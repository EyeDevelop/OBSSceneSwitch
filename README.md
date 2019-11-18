# OBSSceneSwitch
A small project to write a scene to a file. This file can be read by something like the Advanced Scene Switcher plugin for OBS.

If you find this useful, please donate to me :)

**BTC:** 164SdYJi6VEgQqrnbG49RiEL9FzDbR7hUe\
**ETH:** 0xa6e36B2a6d0fE0af3CD6BaAB45daDc595b274B66

## Requirements
* Python3.6+
* pywin32 (Only if on Windows)

## Supported Platforms
* Linux
* Windows

(macOS will probably never be supported because of the weird API for getting a window title.)

## How to Install
1. Download the repo as zip.
1. Run screen_daemon.py.
1. Edit the now generated config file to your liking.
1. Run screen_daemon.py ( for real this time ;) )
1. Configure OBS to switch to the scene by reading the file. (You can use the Advanced Scene Switcher for this)
1. Done!

## The Config File
The default config file ``screens.json`` is as follows:
```json
{
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
}
```

``start_scene (int)``: When you boot screen_daemon.py, it sets the scene to your default scene.\

``unknown_app_scene (str)``: If an app is not listed under window_class or window_name, it will default to this. Set to null if you don't want this auto-switch.\

``delay_time (int)``: The time between scanning the active window. Defaults to 300 ms.\

``window_class``: List of window classes (WM_CLASS with xprop, executable name for Windows).\
|  - ``strict_match (bool)``: Strict matching means the window class / executable has to be EXACTLY the same. Off for checking close resemblance instead.\
|  \
|  - ``scene (str)``: The OBS scene name to switch to when this window_class becomes active.

``window_name``: Same as window class, but matches against window title.
