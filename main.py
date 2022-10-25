"""The central program that ties all the modules together."""

import time
from src.modules.bot import Bot
from src.modules.capture import Capture
from src.modules.notifier import Notifier
from src.modules.listener import Listener
from src.modules.gui import GUI
from src.common import settings
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--full_screen', action='store_true')
    args = parser.parse_args()
    if args.full_screen:
        settings.full_screen = True
        
    bot = Bot()
    capture = Capture()
    notifier = Notifier()
    listener = Listener()

    bot.start()
    while not bot.ready:
        time.sleep(0.01)

    capture.start()
    while not capture.ready:
        time.sleep(0.01)

    notifier.start()
    while not notifier.ready:
        time.sleep(0.01)

    listener.start()
    while not listener.ready:
        time.sleep(0.01)

    print('\n[~] Successfully initialized Auto Maple')

    gui = GUI()
    gui.start()
