from PIL import Image
import mss
import pyautogui


def capture_screen(region=None, save_path=None):
    try:
        session = mss.mss()
        monitor = session.monitors[0] if region is None else {
            "left": region[0],
            "top": region[1],
            "width": region[2],
            "height": region[3],
        }
        raw = session.grab(monitor)
        image = Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")
    except Exception:
        image = pyautogui.screenshot(region=region) if region else pyautogui.screenshot()

    if save_path:
        image.save(save_path)

    return image


def get_screen_size():
    return pyautogui.size()
