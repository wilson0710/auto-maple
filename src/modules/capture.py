"""A module for tracking useful in-game information."""

import time
import cv2
import threading
import ctypes
import mss
import mss.windows
import numpy as np
from src.common import config, utils
from ctypes import wintypes
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT, HWND
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9

# Offset in pixels to adjust for windowed mode
WINDOWED_OFFSET_TOP = 36
WINDOWED_OFFSET_LEFT = 10

# The top-left and bottom-right corners of the minimap
MM_TL_TEMPLATE = cv2.imread('assets/minimap_tl_template.png', 0)
MM_BR_TEMPLATE = cv2.imread('assets/minimap_br_template.png', 0)

MMT_HEIGHT = max(MM_TL_TEMPLATE.shape[0], MM_BR_TEMPLATE.shape[0])
MMT_WIDTH = max(MM_TL_TEMPLATE.shape[1], MM_BR_TEMPLATE.shape[1])

# The player's symbol on the minimap
PLAYER_TEMPLATE = cv2.imread('assets/player_template.png', 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape

GetDC = windll.user32.GetDC
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
GetClientRect = windll.user32.GetClientRect
CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
SelectObject = windll.gdi32.SelectObject
BitBlt = windll.gdi32.BitBlt
SRCCOPY = 0x00CC0020
GetBitmapBits = windll.gdi32.GetBitmapBits
DeleteObject = windll.gdi32.DeleteObject
ReleaseDC = windll.user32.ReleaseDC

class Capture:
    """
    A class that tracks player position and various in-game events. It constantly updates
    the config module with information regarding these events. It also annotates and
    displays the minimap in a pop-up window.
    """

    def __init__(self):
        """Initializes this Capture object's main thread."""

        config.capture = self
        self.capture_gap_sec = 0.03
        self.frame = None
        self.minimap = None
        self.minimap_ratio = 1
        self.minimap_sample = None
        self.sct = None
        self.window = {
            'left': 0,
            'top': 0,
            'width': 1366, # 1366*768 is the default resolution in dev
            'height': 768,
            # 'width': 400, #only need small area at top left
            # 'height': 200,
        }

        self.ready = False
        self.calibrated = False
        self.refresh_counting = 0
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True
        self.handle = user32.FindWindowW(None, "MapleStory")

    def start(self):
        """Starts this Capture's thread."""

        print('\n[~] Started video capture')
        self.thread.start()

    def _main(self):
        """Constantly monitors the player's position and in-game events."""

        mss.windows.CAPTUREBLT = 0
        while True:
            # Calibrate screen capture
            self.handle = user32.FindWindowW(None, "MapleStory")
            # old version for front screenshot
            rect = wintypes.RECT()
            user32.GetWindowRect(self.handle, ctypes.pointer(rect))
            rect = (rect.left, rect.top, rect.right, rect.bottom)
            rect = tuple(max(0, x) for x in rect)

            self.window['left'] = rect[0]
            self.window['top'] = rect[1]
            self.window['width'] = max(rect[2] - rect[0], MMT_WIDTH)
            self.window['height'] = max(rect[3] - rect[1], MMT_HEIGHT)

            # Calibrate by finding the bottom right corner of the minimap
            self.frame = self.screenshot_in_bg(self.handle,0,0,self.window['width'],self.window['height'])
            if self.frame is None:
                continue
            tl, _ = utils.single_match(self.frame, MM_TL_TEMPLATE)
            _, br = utils.single_match(self.frame, MM_BR_TEMPLATE)
            mm_tl = (
                tl[0] + MINIMAP_BOTTOM_BORDER,
                tl[1] + MINIMAP_TOP_BORDER
            )
            mm_br = (
                max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
                max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
            )
            self.minimap_ratio = (mm_br[0] - mm_tl[0]) / (mm_br[1] - mm_tl[1])
            self.minimap_sample = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
            self.calibrated = True
            while True:
                if not self.calibrated:
                    self.refresh_counting = 0
                    break
                # refresh whole game frame every 0.5s
                if self.refresh_counting % 10 == 0:
                  self.frame = self.screenshot_in_bg(self.handle,0,0,self.window['width'],self.window['height'])
                # Take screenshot
                minimap = self.screenshot_in_bg(self.handle,mm_tl[0],mm_tl[1],mm_br[0]-mm_tl[0],mm_br[1]-mm_tl[1])
                if minimap is None:
                    continue

                # Determine the player's position
                player = utils.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
                if player:
                    # config.player_pos = player[0]
                    # print("origin player pos : ",config.player_pos)
                    config.player_pos = utils.convert_to_relative(player[0], minimap)
                    # print("player pos : ",config.player_pos)
                else:
                    if config.player_pos != (0,0): # check is last player_pos near the border
                      pass
              
                # Package display information to be polled by GUI
                self.minimap = {
                    'minimap': minimap,
                    'rune_active': config.bot.rune_active,
                    'rune_pos': config.bot.rune_pos,
                    'path': config.path,
                    'player_pos': config.player_pos
                }

                if not self.ready:
                    self.ready = True
                self.refresh_counting = self.refresh_counting + 1
                time.sleep(self.capture_gap_sec)
                

    def screenshot(self, delay=1):
        try:
            return np.array(self.sct.grab(self.window))
        except mss.exception.ScreenShotError:
            print(f'\n[!] Error while taking screenshot, retrying in {delay} second'
                  + ('s' if delay != 1 else ''))
            time.sleep(delay)
    
    def screenshot_in_bg(self,handle: HWND, tl_x = 0, tl_y = 0, width=0, height=0):
        """窗口客户区截图

        Args:
            handle (HWND): 要截图的窗口句柄

        Returns:
            numpy.ndarray: 截图数据
        """

        if width == 0 or height == 0:
          # get target window size
          r = RECT()
          GetClientRect(handle, byref(r))
          width, height = r.right, r.bottom

        # 开始截图
        dc = GetDC(handle)
        cdc = CreateCompatibleDC(dc)
        bitmap = CreateCompatibleBitmap(dc, width, height)
        SelectObject(cdc, bitmap)
        BitBlt(cdc, 0, 0, width, height, dc, tl_x, tl_y, SRCCOPY)
        # 截图是BGRA排列，因此总元素个数需要乘以4
        total_bytes = width*height*4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte*total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))
        DeleteObject(bitmap)
        DeleteObject(cdc)
        ReleaseDC(handle, dc)
        # 返回截图数据为numpy.ndarray
        return np.frombuffer(buffer, dtype=np.uint8).reshape(height, width, 4)