import time

import win32gui
import win32process
import wmi

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
    except:
        return None
    else:
        return exe


def get_app_name(hwnd):
    """Get applicatin filename given hwnd."""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query(
            "SELECT Name FROM Win32_Process WHERE ProcessId = %s" % str(pid)
        ):
            exe = p.Name
            name_without_ext = exe.split(".")[:-1]
            name_without_ext = " ".join(name_without_ext)
            break
    except:
        return None
    else:
        return exe, name_without_ext


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
            # TODO: find out later on what if the workspace have a "-" in their name
            workspace = title.split("—")[0].strip()
            active_file = title.split("—")[1].strip()

            return {
                "type": "Coding",
                "workspace": workspace,
                "active_file": active_file,
            }

        if window_name in ["msedge", "chrome", "firefox"]:
            return {"type": "browsing", "title": title}

    except Exception as e:
        print(f"error {e}")
        return None


while True:
    window = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(window)

    if title != last_title:
        print("\n")
        _, active_window_name = get_app_name(window)

        activity_window_and_title = f"{active_window_name}: {title}"

        print(f"Current Activity: {activity_window_and_title}")

        print(classify_activity(activity_window_and_title))
        last_title = title

    time.sleep(1)
