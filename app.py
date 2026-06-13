import os
import time

import requests
import win32gui
import win32process
import wmi
from dotenv import load_dotenv

load_dotenv()

GH_TOKEN = os.getenv("GITHUB_TOKEN")

last_title = ""

c = wmi.WMI()


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
        exe, name_without_ext = "", ""
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query(
            "SELECT Name FROM Win32_Process WHERE ProcessId = %s" % str(pid)
        ):
            exe = p.Name
            name_without_ext = exe.split(".")[:-1]
            name_without_ext = " ".join(name_without_ext)
            break

        return exe, name_without_ext

    except:
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
            video_title = ""
            if "youtube" in title.lower():
                video_title = title.split("-")[0].strip()
                print(video_title)
                return {"type": "Youtube", "title": video_title, "emoji": "red_circle"}
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


while True:
    window = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(window)

    if title != last_title:
        print("\n")
        _, active_window_name = get_app_name(window)

        activity_window_and_title = f"{active_window_name}: {title}"

        print(f"Current Activity: {activity_window_and_title}")

        classified_activity = classify_activity(activity_window_and_title)
        last_title = title

        if classified_activity is None:
            continue

        update_github_status(classified_activity)

    time.sleep(1)
