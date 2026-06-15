import os
import threading
import time

import psutil
import requests
import win32gui
import win32process
from dotenv import load_dotenv
from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS

load_dotenv()

GH_TOKEN = os.getenv("GITHUB_TOKEN")

# c = wmi.WMI()

app = Flask(__name__)
CORS(app)

activities = {"coding": {}, "youtube": {}, "browsing": {}, "others": {}}

# def get_app_path(hwnd):
#     """Get applicatin path given hwnd."""
#     try:
#         _, pid = win32process.GetWindowThreadProcessId(hwnd)
#         for p in c.query(
#             "SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s" % str(pid)
#         ):
#             exe = p.ExecutablePath
#             break
#         return exe

#     except:
#         return None


def get_app_name(hwnd):
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        process = psutil.Process(pid)
        exe = process.name()

        name_without_ext = exe.split(".")[:-1]
        name_without_ext = " ".join(name_without_ext)

        return exe, name_without_ext

    except Exception as e:
        print(e)
        return None


def classify_activity(app_name, title):
    """
    activity_window_and_title sample value:
    if not yt:
        Zed gives this kind of title
            Zed: acsense — app.py
        But VsCode just gives
            Visual Studio Code

    if yt:
            Green Day - American Idiot [Official Music Video] [4K Upgrade] - YouTube
    """
    # title = activity_window_and_title
    # split = activity_window_and_title.split(":")
    # window_name = split[0]

    # if not other_apps:
    #     title = split[1].strip()

    try:
        print("app_nameapp_nameapp_nameapp_name", app_name)
        if app_name == "Zed" or app_name == "Code":
            global activities
            # workspace = title.split("—")[0].strip() if title.split("—")[0].strip()  else ""
            # active_file = title.split("—")[1].strip() if title.split("—")[1].strip() else ""

            activities["coding"]["type"] = "coding"
            activities["coding"]["description"] = f"Coding on {title}"
            # activities["coding"]["workspace"] = title
            # activities["coding"]["active_file"] = "Coding"
            activities["coding"]["emoji"] = "computer"

        elif app_name in ["msedge", "chrome", "firefox"]:
            activities["browsing"] = {
                "type": "browsing",
                "description": f"Browsing on {app_name}",
                "emoji": "globe_with_meridians",
            }

        else:
            activities["others"] = {
                "type": "Others",
                "description": title,
                "emoji": "sloth",
            }

    except Exception as e:
        print(f"error {e}")
        return None


def update_github_status(classified_activity):
    """
    expects
    if zed | vscode {
            "type": "Coding",
            "workspace": ...,
            "active_file": ...,
            "emoji": "...",
    }

    if youtube {
            "type": "Youtube",
            "title": ...,
            "emoji": "...",
    }
    """

    query = f"""
    mutation {{
    changeUserStatus(input: {{
        emoji: ":{classified_activity["emoji"]}:",
        message: "{classified_activity["description"] if classified_activity["type"] in ["coding", "Coding"] else (f"{classified_activity['description']}" if classified_activity["type"] == "Youtube" else (classified_activity["title"] if classified_activity["type"] == "others" else classified_activity["description"]))}"
    }}) {{
        status {{
        message
        }}
    }}
    }}
    """

    headers = {"Authorization": f"Bearer {GH_TOKEN}"}

    requests.post(
        "https://api.github.com/graphql",
        json={"query": query},
        headers=headers,
    )


last_title = ""
youtube_video = ""
last_youtube_video = ""


@app.route("/youtube-activity", methods=["POST"])
def activity():
    global activities
    """
	sample output:
		log:  127.0.0.1 - - [14/Jun/2026 08:48:14] "POST /youtube-activity HTTP/1.1" 200
		title: Green Day - American Idiot [Official Music Video] [4K Upgrade] - YouTube

	"""
    try:
        if request.is_json:
            global youtube_video
            data = request.get_json()

            title = data.get("title")
            youtube_video = title.removesuffix(" - YouTube")

            activities["youtube"] = {
                "type": "Youtube",
                "description": f"Watching {youtube_video}",
                "emoji": "red_circle",
            }

            return jsonify({"success": True, "title": title})

        return jsonify({"success": False})

    except Exception as e:
        print(e)


def worker():
    while True:
        global last_title, youtube_video, last_youtube_video
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        print(title)

        if (
            title == "Task Switching"
            or title == "Start Menu"
            or title == "Windows Search"
            or title == "Notification Center"
            or title == ""
        ):
            print(f"Ignored window: {title}")
            continue

        """
		priority:
			1. Coding (Zed, Visual Studio Code)
			2. Youtube
			3. Browsing

		this updates to youtube status only IF Zed or VsCode is not running in the process.
		"""

        if get_app_name(window) is None:
            break

        exe, app_name = get_app_name(window)

        print("app_name", app_name)
        print("exe", exe)

        if title != last_title:
            last_title = title

            # activity_window_and_title = f"{app_name}: {title}"
            classify_activity(app_name, title)
            print(exe)

            # exe name for zed and vscode are: Zed.exe and Code.exe
            if app_name == "Zed" or app_name == "Code":
                activities["coding"]["process_name"] = exe

            print(activities)
            # ...
            if activities["coding"]:
                found = False
                processes = psutil.process_iter()

                for p in processes:
                    # print(
                    #     f"comparing {activities['coding']['process_name']} to {p.name()}"
                    # )
                    if p.name() == activities["coding"]["process_name"]:
                        found = True
                        break
                if not found:
                    activities["coding"] = None

                else:
                    update_github_status(activities["coding"])

            elif activities["youtube"]:
                update_github_status(activities["youtube"])
            elif activities["browsing"]:
                update_github_status(activities["browsing"])
            else:
                update_github_status(activities["others"])
            # ...

        time.sleep(1)


thread = threading.Thread(target=worker)
thread.start()
