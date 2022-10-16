"""A module for tracking useful in-game information."""

import time
import cv2
import threading
import ctypes
import mss
import mss.windows
import numpy as np
from src.common import config, utils, settings
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
        self.capture_gap_sec = 0.02
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
        self.default_window_resolution = {
            '1366':(1366,768),
            '1280':(1280,720)
        }
        self.latest_positions = []
        self.MAX_LATEST_POSITION_AMOUNT = 10
        self.recording_frames = []
        self.MAX_RECORDING_AMOUNT = 60
        self.ready = False
        self.calibrated = False
        self.refresh_counting = 0
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True
        self.handle = user32.FindWindowW(None, "MapleStory")
        self.check_is_standing_count = 0
        
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

            if abs(self.default_window_resolution['1366'][0] - self.window['width']) < \
                    abs(self.default_window_resolution['1280'][0] - self.window['width']):
                # self.window['left'] = rect[0] + (self.default_window_resolution['1366'][0] - self.window['width'])
                self.window['top'] = rect[1] + abs(self.default_window_resolution['1366'][1] - self.window['height'])
                self.window['width'] = self.default_window_resolution['1366'][0]
                self.window['height'] = self.default_window_resolution['1366'][1]
            else:
                # self.window['left'] = rect[0] + (self.default_window_resolution['1280'][0] - self.window['width'])
                self.window['top'] = rect[1] + abs(self.default_window_resolution['1280'][1] - self.window['height'])
                self.window['width'] = self.default_window_resolution['1280'][0]
                self.window['height'] = self.default_window_resolution['1280'][1]

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
            self.check_is_standing_count = 0

            while True:
                if not self.calibrated:
                    self.refresh_counting = 0
                    break
                # refresh whole game frame every 0.5s
                if self.refresh_counting % 5 == 0:
                    self.frame = self.screenshot_in_bg(self.handle,0,0,self.window['width'],self.window['height'])
                    
                # save pic every 1s, max 60 pic
                if self.refresh_counting % 100 == 0 and config.enabled:
                    self.recording_frames.append(self.frame)
                    if len(self.recording_frames) > self.MAX_RECORDING_AMOUNT:
                        self.recording_frames.pop(0)
                elif not config.enabled and len(self.recording_frames) > 0:
                    for index in range(len(self.recording_frames)):
                        cv2.imwrite('./recording/' + str(index) + '.png',self.recording_frames[index])

                # Take screenshot
                minimap = self.screenshot_in_bg(self.handle,mm_tl[0],mm_tl[1],mm_br[0]-mm_tl[0],mm_br[1]-mm_tl[1])
                if minimap is None:
                    continue
                
                # Determine the player's position
                player = utils.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
                if player:
                    # check is_standing
                    last_player_pos = config.player_pos
                    config.player_pos = utils.convert_to_relative(player[0], minimap)
                    done_check_is_standing = False
                    is_bottom = False
                    # print(config.player_pos)
                    # record if latest postion has been changed
                    if last_player_pos != config.player_pos or self.refresh_counting % 5 == 0:
                        self.latest_positions.append(config.player_pos)
                        if len(self.latest_positions) > self.MAX_LATEST_POSITION_AMOUNT:
                            self.latest_positions.pop(0)

                    # check is_standing by settins.platforms
                    if settings.platforms != '':
                        temp_platforms = settings.platforms.split("|")
                        for platform_y in temp_platforms:
                            check_is_bottom = platform_y.split("b")
                            if len(check_is_bottom) == 2:
                                temp_xy = check_is_bottom[1].split("*")
                                platform_y = check_is_bottom[1]
                                is_bottom = True
                            else:
                                temp_xy = platform_y.split("*")
                            if len(temp_xy) == 1:
                                if abs(int(platform_y) - int(config.player_pos[1])) <= 0:
                                    config.player_states['is_standing'] = True
                                    config.player_states['movement_state'] = config.MOVEMENT_STATE_STANDING
                                    done_check_is_standing = True
                                    if is_bottom:
                                        config.player_states['in_bottom_platform'] = True
                                    else:
                                        config.player_states['in_bottom_platform'] = False
                                    break
                            else:
                                temp_x_range = temp_xy[0].split("~")
                                if abs(int(platform_y) - int(config.player_pos[1])) <= 0\
                                        and (int(temp_x_range[1]) > config.player_pos[0] and int(temp_x_range[0]) < config.player_pos[0]): 
                                    config.player_states['is_standing'] = True
                                    config.player_states['movement_state'] = config.MOVEMENT_STATE_STANDING
                                    done_check_is_standing = True
                                    if is_bottom:
                                        config.player_states['in_bottom_platform'] = True
                                    else:
                                        config.player_states['in_bottom_platform'] = False
                                    break
                        config.player_states['in_bottom_platform'] = True
                    if last_player_pos[1] == config.player_pos[1] and not config.player_states['is_standing']:
                        self.check_is_standing_count += 1
                        if self.check_is_standing_count >= 7:
                            config.player_states['is_standing'] = True
                            config.player_states['movement_state'] = config.MOVEMENT_STATE_STANDING
                            self.check_is_standing_count = 0
                            print('back to ground')
                    elif last_player_pos[1] != config.player_pos[1] and done_check_is_standing == False:
                        self.check_is_standing_count = 0
                        config.player_states['is_standing'] = False
                        if last_player_pos[1] < config.player_pos[1]:
                            config.player_states['movement_state'] = config.MOVEMENT_STATE_FALLING
                        else:
                            config.player_states['movement_state'] = config.MOVEMENT_STATE_JUMPING
                else:
                    if config.player_pos != (0,0): # check is last player_pos near the border
                        if config.player_pos[1] < 10:
                            config.player_states['movement_state'] = config.MOVEMENT_STATE_JUMPING
                            config.player_pos = (config.player_pos[0],0)
                        if config.player_pos[0] < 30:
                            config.player_pos = (0,config.player_pos[1])
                            config.player_states['is_standing'] = True
                            config.player_states['movement_state'] = config.MOVEMENT_STATE_STANDING
                        elif int(minimap.shape[1]) - config.player_pos[0] < 30:
                            config.player_pos = (int(minimap.shape[1]),config.player_pos[1])
                            config.player_states['is_standing'] = True
                            config.player_states['movement_state'] = config.MOVEMENT_STATE_STANDING
                


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