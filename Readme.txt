# Video Soundboard

## Overview

Video Soundboard is a lightweight Python application designed to control **OBS Studio** through its WebSocket interface.

The application does **not** play videos, decode media files or perform any graphical rendering. All media playback, video rendering, audio mixing and recording are entirely handled by OBS Studio.

The Python application simply acts as a remote controller that listens for keyboard shortcuts and sends commands to OBS.

The project has been intentionally designed to remain simple, easy to understand and easy to extend.

---

# Features

Current version features:

* Load a JSON configuration file at startup.
* Connect to OBS Studio through the WebSocket API.
* Register global keyboard shortcuts.
* Control multiple video sources.
* Change the position of a source.
* Change the scale of a source.
* Apply a rotation.
* Adjust the audio volume.
* Restart media playback each time a shortcut is pressed.
* Automatically hide a source when playback finishes.
* Support multiple videos sharing the same keyboard shortcut.

No graphical user interface is provided.

All configuration is performed by editing a single JSON file.

---

# Project Structure

```text
VideoSoundboard/

└── src/
    └── main.py
    └── obs.py
    └── config.py
└── config/
    └── config.json
└── Readme.txt
└── requirements.txt
```

### main.py

Application entry point.

Responsible for:

* loading the configuration;
* initializing OBS;
* starting the keyboard listener;
* coordinating the application.

---

### config.py

Configuration management.

Responsible for:

* reading `config.json`;
* validating its contents;
* creating the `Sound` objects used by the application.

---

### obs.py

OBS communication layer.

Responsible for:

* WebSocket connections;
* source lookup;
* Scene Item initialization;
* transformations;
* media control;
* event handling;
* keyboard shortcuts.

---

# Configuration

The application is configured through:

```text
config/config.json
```

Each entry describes one independent video source.

Example:

```json
{
    "name": "Video1",
    "scene": "SCENE_VIDEO_SOUNDBOARD",
    "source": "SRC_VIDEO1",
    "hotkey": "<alt>+1",
    "x": 250,
    "y": 300,
    "scale_x": 1.0,
    "scale_y": 1.0,
    "rotation": 0,
    "volume": 80
}
```

Each source contains:

* a display name;
* the OBS scene;
* the OBS media source;
* the keyboard shortcut;
* the position;
* the scale;
* the rotation;
* the playback volume.

Adding a new video only requires adding a new entry to this file.

No modification of the Python source code is required.

---

# OBS Studio Setup

Before running the application, OBS Studio must be configured correctly.

Requirements:

* OBS Studio installed.
* OBS WebSocket server enabled.
* The WebSocket password configured in the Python application.
* A scene named:

```text
SCENE_VIDEO_SOUNDBOARD
```

All video sources must be placed inside this scene.

Each source must:

* be an OBS Media Source;
* use a unique source name;
* match the corresponding `source` field in `config.json`;
* be initially hidden;
* have loop playback disabled;
* be controllable through OBS WebSocket.

The application never creates or modifies OBS sources.

Only existing sources are controlled.

---

# How the Application Works

When the application starts:

1. The configuration file is loaded.
2. A connection to OBS Studio is established.
3. The EventClient is initialized.
4. Every configured source is located inside OBS.
5. Each Scene Item ID is stored.
6. Keyboard shortcuts are registered.
7. The application waits for user input.

When a keyboard shortcut is pressed:

1. The corresponding video(s) are identified.
2. The source transformation is updated.
3. The volume is adjusted.
4. The source becomes visible.
5. Media playback restarts from the beginning.

When playback finishes:

1. OBS sends a `MediaInputPlaybackEnded` event.
2. The application receives the event.
3. The corresponding source is automatically hidden.

---

# Installation

## Requirements

* Python 3.12 or newer
* Linux
* OBS Studio
* OBS WebSocket enabled

Required Python packages:

* obsws-python
* pynput

Install them using pip:

```bash
pip install obsws-python pynput
```

---

# Running the Application

Start OBS Studio.

Verify that the WebSocket server is enabled.

Check that all media sources defined in `config.json` exist inside OBS.

Run the application:

```bash
python3 main.py
```

The application will remain running and wait for keyboard shortcuts.

Press the configured shortcut to trigger one or more videos.

Terminate the program with:

```text
Ctrl+C
```

The application will close the WebSocket connections before exiting.

---

# Error Handling

The application immediately stops execution if one of the following errors occurs:

* configuration file not found;
* invalid JSON file;
* missing mandatory field;
* OBS connection failure;
* missing OBS scene;
* missing OBS source;
* invalid keyboard shortcut.

Each error produces a clear and explicit error message.

---

# Design Philosophy

This project follows a minimal architecture.

Each module has a single responsibility.

The application is intentionally kept simple to facilitate maintenance and future extensions.

Its primary objective is to provide a lightweight and reliable controller for OBS Studio while keeping the Python code clean, readable and easy to evolve.

