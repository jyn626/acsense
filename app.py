import os
import threading
import time

import psutil
import requests
import win32gui
import win32process
import wmi
from dotenv import load_dotenv
from flask import Flask, request
from flask.json import jsonify
from flask_cors import CORS

load_dotenv()

GH_TOKEN = os.getenv("GITHUB_TOKEN")


c = wmi.WMI()

app = Flask(__name__)
CORS(app)

activities = {"coding": None, "youtube": None, "browsing": None, "others": None}


def get_app_path(hwnd):
    """Get applicatin path given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query(
            "SELECT ExecutablePath FROM Win32_Process WHERE ProcessId = %s" % str(pid)
        ):
            exe = p.ExecutablePath
            break
        return exe

    except:
        return None


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


def classify_activity(activity_window_and_title, other_apps=False):
    """
    activity_window_and_title sample value:
    if not yt:
            Zed: acsense — app.py
    if yt:
            Green Day - American Idiot [Official Music Video] [4K Upgrade] - YouTube
    """
    title = activity_window_and_title
    split = activity_window_and_title.split(":")
    window_name = split[0]

    # if not other_apps:
    #     title = split[1].strip()

    try:
        if window_name == "Zed" or window_name == "Visual Studio Code":
            global activities
            # TODO: fix cases where the workspace name have "—"
            workspace = title.split("—")[0].strip()
            active_file = title.split("—")[1].strip()

            activities["coding"] = {
                "type": "Coding",
                "workspace": workspace,
                "active_file": active_file,
                "emoji": "computer",
            }

        elif window_name in ["msedge", "chrome", "firefox"]:
            activities["browsing"] = {
                "type": "Browsing",
                "title": title,
                "emoji": "globe_with_meridians",
            }

        else:
            activities["others"] = {"type": "Others", "title": title, "emoji": "sloth"}

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
		message: "{f"Coding {classified_activity["workspace"]} — {classified_activity["active_file"]}" if classified_activity["type"] == "Coding" else (f"YT - {classified_activity["title"]}" if classified_activity["type"] == "Youtube" else classified_activity["title"])}"
	  }}) {{
		status {{
		  message
		}}
	  }}
	}}
	"""

    headers = {"Authorization": f"Bearer {GH_TOKEN}"}

    response = requests.post(
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
                "title": youtube_video,
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
        """
		priority:
			1. Coding (Zed, Visual Studio Code)
			2. Youtube
			3. Browsing

		this updates to youtube status only IF Zed or VsCode is not running in the process.
		"""

        exe, app_name = get_app_name(window)

        if app_name is None:
            break

        if title != last_title:
            last_title = title

            activity_window_and_title = f"{app_name}: {title}"
            classify_activity(activity_window_and_title)

            if "zed" in app_name.lower():
                activities["coding"]["process_name"] = exe

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
                        print("Zed opened")
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
