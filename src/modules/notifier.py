"""A module for detecting and notifying the user of dangerous in-game events."""

from msilib.schema import Component
from src.common import config, utils, settings
import time
import os
import cv2
import pygame
import threading
import numpy as np
import keyboard as kb
import requests
from src.common.vkeys import key_down, key_up, press, click
from src.routine.components import Point


# A rune's symbol on the minimap
RUNE_RANGES = (
    ((141, 148, 245), (146, 158, 255)),
)
rune_filtered = utils.filter_color(cv2.imread('assets/rune_template.png'), RUNE_RANGES)
RUNE_TEMPLATE = cv2.cvtColor(rune_filtered, cv2.COLOR_BGR2GRAY)

# Other players' symbols on the minimap
OTHER_RANGES = (
    ((0, 245, 215), (10, 255, 255)),
)
other_filtered = utils.filter_color(cv2.imread('assets/other_template.png'), OTHER_RANGES)
OTHER_TEMPLATE = cv2.cvtColor(other_filtered, cv2.COLOR_BGR2GRAY)

# The Elite Boss's warning sign
ELITE_TEMPLATE = cv2.imread('assets/elite_template2.jpg', 0)

# check for unexpected conversation
STOP_CONVERSTION_TEMPLATE = cv2.imread('assets/stop_conversation.jpg', 0)

# check for unexpected conversation
REVIVE_CONFIRM_TEMPLATE = cv2.imread('assets/revive_confirm.png', 0)

# fiona_lie_detector image
FIONA_LIE_DETECTOR_TEMPLATE = cv2.imread('assets/fiona_lie_detector.png',0)

def get_alert_path(name):
    return os.path.join(Notifier.ALERTS_DIR, f'{name}.mp3')


class Notifier:
    ALERTS_DIR = os.path.join('assets', 'alerts')

    def __init__(self):
        """Initializes this Notifier object's main thread."""

        pygame.mixer.init()
        self.mixer = pygame.mixer.music

        self.ready = False
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

        self.room_change_threshold = 0.9
        self.rune_alert_delay = 270         # 4.5 minutes
        self.notifier_delay = 0.1
        self.skill_template_cd_set = {}

    def start(self):
        """Starts this Notifier's thread."""

        print('\n[~] Started notifier')
        self.thread.start()

    def _main(self):
        self.ready = True
        prev_others = 0
        rune_start_time = time.time()
        detection_i = 0
        while True:
            if config.enabled:
                frame = config.capture.frame
                height, width, _ = frame.shape
                minimap = config.capture.minimap['minimap']

                # Check for unexpected black screen
                if not config.map_changing:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    if np.count_nonzero(gray < 15) / height / width > self.room_change_threshold:
                        self._send_msg_to_line_notify("畫面黑屏")
                        if settings.rent_frenzy == False:
                            self._alert('siren')

                # Check for elite warning
                elite_frame = frame[height // 4:3 * height // 4, width // 4:3 * width // 4]
                elite = utils.multi_match(elite_frame, ELITE_TEMPLATE, threshold=0.9)
                if len(elite) > 0:
                    self._send_msg_to_line_notify("黑王出沒")
                    if settings.rent_frenzy == False:
                        self._alert('siren')

                # Check for other players entering the map
                filtered = utils.filter_color(minimap, OTHER_RANGES)
                others = len(utils.multi_match(filtered, OTHER_TEMPLATE, threshold=0.5))
                config.stage_fright = others > 0
                if others != prev_others:
                    if others > prev_others:
                        self._ping('ding')
                    prev_others = others

                # check for fiona_lie_detector
                fiona_frame = frame[height-400:height, width - 300:width]
                fiona_lie_detector = utils.multi_match(fiona_frame, FIONA_LIE_DETECTOR_TEMPLATE, threshold=0.9)
                if len(fiona_lie_detector) > 0:
                    print("find fiona_lie_detector")
                    self._send_msg_to_line_notify("菲歐娜測謊")
                    # if settings.rent_frenzy == False:
                    self._alert('siren')
                    time.sleep(0.1)
                    
                # not urgen detection 
                if detection_i % 5==0:
                    # check for unexpected conversation
                    conversation_frame = frame[height//2-250:height//2+250, width //2-250:width//2+250]
                    conversation = utils.multi_match(conversation_frame, STOP_CONVERSTION_TEMPLATE, threshold=0.9)
                    if len(conversation) > 0:
                        print("stop conversation")
                        press("esc",1)
                        time.sleep(0.1)

                    # check for unexpected dead
                    revive_frame = frame[height//2-100:height//2+200, width //2-150:width//2+150]
                    revive_confirm = utils.multi_match(revive_frame, REVIVE_CONFIRM_TEMPLATE, threshold=0.9)
                    if len(revive_confirm) > 0:
                        self._send_msg_to_line_notify("角色死亡")
                        revive_confirm_pos = min(revive_confirm, key=lambda p: p[0])
                        target = (
                            round(revive_confirm_pos[0] + config.capture.window['left']+(width //2-150)),
                            round(revive_confirm_pos[1] + config.capture.window['top']+(height//2-100))
                        )
                        click(target, button='left')
                        time.sleep(3)
                        click((700,100), button='right')

                
                # Check for skill cd
                command_book = config.bot.command_book
                image_matched = False
                for key in command_book:
                    if hasattr(command_book[key],"skill_cool_down"):
                        command_book[key].get_is_skill_ready()
                    if hasattr(command_book[key],"skill_image") and image_matched == False and not command_book[key].get_is_skill_ready():
                        if not key in self.skill_template_cd_set:
                            skill_template = cv2.imread(command_book[key].skill_image, 0)
                            self.skill_template_cd_set[key] = skill_template
                        else:
                            skill_template = self.skill_template_cd_set[key]
                        is_ready_region = frame[height-500:height-90, width-182:width-126]
                        skill_match = utils.multi_match(is_ready_region, skill_template, threshold=0.9)
                        if len(skill_match) > 0:
                            print(command_book[key]._display_name , " skill_match")
                            # image_matched = True
                            command_book[key].set_is_skill_ready(True)

                # Check for rune
                now = time.time()
                if settings.rent_frenzy == False:
                    if not config.bot.rune_active:
                        filtered = utils.filter_color(minimap, RUNE_RANGES)
                        matches = utils.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
                        rune_start_time = now
                        if matches and config.routine.sequence:
                            abs_rune_pos = (matches[0][0], matches[0][1])
                            config.bot.rune_pos = utils.convert_to_relative(abs_rune_pos, minimap)
                            print('rune pos : ',config.bot.rune_pos)
                            distances = list(map(distance_to_rune, config.routine.sequence))
                            index = np.argmin(distances)
                            config.bot.rune_closest_pos = config.routine[index].location
                            config.bot.rune_active = True
                            self._ping('rune_appeared', volume=0.75)
                    elif now - rune_start_time > self.rune_alert_delay:     # Alert if rune hasn't been solved
                        config.bot.rune_active = False
                        self._send_msg_to_line_notify("多次解輪失敗")
                        self._alert('siren')
                detection_i = detection_i + 1
            time.sleep(self.notifier_delay)

    def _send_msg_to_line_notify(self,msg,file=None):
        url = "https://notify-api.line.me/api/notify"
        if settings.id == "veg":
            token = "ezvoLebyYzo6yYlh1BbcF0pab4gU2pWBBG8S0QzkysA"
        else:
            token = "gOgNCkc4PLinHFzJSbqQZHQyLotFuu0skBCFmHicKoZ"
        my_headers = {'Authorization': 'Bearer ' + token }
        data = {"message" : msg }
        if file:
            image = open(file, 'rb')    # 以二進位方式開啟圖片
            imageFile = {'imageFile' : image}   # 設定圖片資訊
            r = requests.post(url,headers = my_headers, data = data, files=imageFile)
        else:
            r = requests.post(url,headers = my_headers, data = data)

    def _alert(self, name, volume=0.6):
        """
        Plays an alert to notify user of a dangerous event. Stops the alert
        once the key bound to 'Start/stop' is pressed.
        """

        config.enabled = False
        config.listener.enabled = False
        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play()
        # use go home scroll
        # kb.press("f9")

        while not kb.is_pressed(config.listener.config['Start/stop']):
            time.sleep(0.1)
        self.mixer.stop()
        time.sleep(2)
        config.listener.enabled = True

    def _ping(self, name, volume=0.5):
        """A quick notification for non-dangerous events."""

        self.mixer.load(get_alert_path(name))
        self.mixer.set_volume(volume)
        self.mixer.play()


#################################
#       Helper Functions        #
#################################
def distance_to_rune(point):
    """
    Calculates the distance from POINT to the rune.
    :param point:   The position to check.
    :return:        The distance from POINT to the rune, infinity if it is not a Point object.
    """

    if isinstance(point, Point):
        return utils.distance(config.bot.rune_pos, point.location)
    return float('inf')
