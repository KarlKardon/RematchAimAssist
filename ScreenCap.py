from mss import mss
import numpy as np
import cv2
import ctypes

# ─── Configuration ─────────────────────────────────────────────────────────────

# adjust these to match your minimap size & padding
MINI_W, MINI_H     = 460, 460
PADDING_X, PADDING_Y = 57, 57

# HSV range for your teammate color
lower_hsv = np.array([  4, 150,  20])
upper_hsv = np.array([ 20, 255, 100])

# Overlay window settings
OVERLAY_SIZE = 300
ARROW_LENGTH = 120
ARROW_COLOR  = (0,255,0)  # green arrow
ARROW_THICK  = 4
ARROW_TIPLEN = 0.3

# Win32 flags for SetWindowPos
SWP_NOSIZE     = 0x0001
SWP_NOACTIVATE = 0x0010
HWND_TOPMOST   = -1

# Desired on‑screen position for the overlay window
# (adjust X, Y to where you want the top‑left corner)
X, Y = 100, 100

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    # 1) Create & size the overlay window
    cv2.namedWindow("Overlay", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Overlay", OVERLAY_SIZE, OVERLAY_SIZE)

    # 2) Grab its HWND and set it top‑most at (X, Y) without activating or resizing
    hwnd = ctypes.windll.user32.FindWindowW(None, "Overlay")
    ctypes.windll.user32.SetWindowPos(
        hwnd, HWND_TOPMOST,
        X, Y,       # move to (X, Y)
        0, 0,       # zero width/height (ignored by SWP_NOSIZE)
        SWP_NOSIZE | SWP_NOACTIVATE
    )

    # ─── Make the OpenCV window layered + transparent by color key ───

    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    LWA_COLORKEY = 0x00000001  # use BLACK (0x000000) as the transparent color

    # 1) turn on layered style
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(
        hwnd, GWL_EXSTYLE,
        style | WS_EX_LAYERED
    )

    # 2) tell Windows “treat pure black as transparent”
    ctypes.windll.user32.SetLayeredWindowAttributes(
        hwnd,
        0x000000,  # the COLORKEY (black)
        0,  # alpha (unused with COLORKEY)
        LWA_COLORKEY
    )

    with mss() as sct:
        mon = sct.monitors[1]
        screen_w, screen_h = mon["width"], mon["height"]
        region = {
            "top":    screen_h - MINI_H - PADDING_Y,
            "left":   screen_w  - MINI_W - PADDING_X,
            "width":  MINI_W,
            "height": MINI_H
        }

        while True:
            # 3) Ensure window stays top‑most each frame
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST,
                X, Y, 0, 0,
                SWP_NOSIZE | SWP_NOACTIVATE
            )

            # 4) grab minimap
            img_bgra = np.array(sct.grab(region))
            bgr      = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)

            # 5) threshold teammate blips
            hsv  = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
            mask = cv2.morphologyEx(mask,
                                    cv2.MORPH_OPEN,
                                    np.ones((3,3), np.uint8),
                                    iterations=1)

            # 6) find blobs
            cnts, _ = cv2.findContours(mask,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
            h, w    = mask.shape

            # 7) prepare blank overlay image
            overlay = np.zeros((OVERLAY_SIZE, OVERLAY_SIZE, 3),
                               dtype=np.uint8)
            center = (OVERLAY_SIZE//2, OVERLAY_SIZE//2)

            for cnt in cnts:
                M = cv2.moments(cnt)
                if not M["m00"]:
                    continue

                cx = int(M["m10"]/M["m00"])
                cy = int(M["m01"]/M["m00"])

                # skip your own player near center
                if np.hypot(cx - w/2, cy - h/2) < 20:
                    continue

                # compute direction → angle
                dx = cx - w/2
                dy = cy - h/2
                angle = np.arctan2(dy, dx)

                # debug draw on minimap
                cv2.circle(bgr, (cx, cy), 4, (0,0,255), -1)
                cv2.arrowedLine(
                    bgr,
                    (w//2, h//2),
                    (int(w/2 + dx*1.2), int(h/2 + dy*1.2)),
                    (0,0,255), 2, tipLength=0.3
                )

                # draw arrow in overlay window
                end_pt = (
                    int(center[0] + np.cos(angle)*ARROW_LENGTH),
                    int(center[1] + np.sin(angle)*ARROW_LENGTH)
                )
                cv2.arrowedLine(
                    overlay,
                    center,
                    end_pt,
                    ARROW_COLOR,
                    ARROW_THICK,
                    tipLength=ARROW_TIPLEN
                )

            # 8) show windows
            cv2.imshow("Minimap Detection", bgr)
            cv2.imshow("Overlay", overlay)

            if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
