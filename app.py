import json
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


def classify_activity(activity_window_and_title):
    """
    Sample activity_window_and_title content: Zed: acsense — app.py
    split = ["Zed", "acsense - app.py"]
    """
    split = activity_window_and_title.split(":")
    window_name = split[0]
    title = split[1].strip()

    try:
        if window_name == "Zed" or window_name == "Visual Studio Code":
            # TODO: fix cases where the workspace name have "—"
            workspace = title.split("—")[0].strip()
            active_file = title.split("—")[1].strip()

            return {
                "type": "Coding",
                "workspace": workspace,
                "active_file": active_file,
                "emoji": "computer",
            }

        if window_name in ["msedge", "chrome", "firefox"]:
            # video_title = ""
            # if "youtube" in title.lower():
            #     video_title = title.split("-")[0].strip()
            #     print(video_title)
            #     return {"type": "Youtube", "title": video_title, "emoji": "red_circle"}
            return {"type": "Browsing", "title": title, "emoji": "globe_with_meridians"}

    except Exception as e:
        print(f"error {e}")
        return None


def update_github_status(classified_activity):
    query = f"""
	mutation {{
	  changeUserStatus(input: {{
		emoji: ":{classified_activity["emoji"]}:",
		message: "{f"Coding {classified_activity["workspace"]} — {classified_activity["active_file"]}" if classified_activity["type"] == "Coding" else (f"YT - {classified_activity["title"]}" if classified_activity["type"] == "Youtube" else classified_activity["type"])}"
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


@app.route("/youtube-activity", methods=["POST"])
def activity():
    try:
        if request.is_json:
            data = request.get_json()

            title = data.get("title")
            # url = data.get("url")
            print(title)
            return jsonify({"success": True, "title": title})
        print("im here")
        return jsonify({"success": False})

    except Exception as e:
        print(e)


last_title = ""


def worker():
    while True:
        global last_title
        print("thread")
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)

        if title != last_title:
            last_title = title
            # print("\n")
            # print(title)
            # print("app name")
            # print(get_app_name(window))
            if get_app_name(window) is None:
                continue

            _, active_window_name = get_app_name(window)

            activity_window_and_title = f"{active_window_name}: {title}"

            print(f"Current Activity: {activity_window_and_title}")

            classified_activity = classify_activity(activity_window_and_title)
            last_title = title

            if classified_activity is None:
                continue

            update_github_status(classified_activity)

        time.sleep(1)


thread = threading.Thread(target=worker)
thread.start()
