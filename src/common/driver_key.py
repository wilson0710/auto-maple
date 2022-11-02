# -*- coding: utf-8 -*-
from ctypes import CDLL
from time import sleep
import os
import threading

driver_dir_path = r'driver'
kmclass_dll_path = os.path.abspath(driver_dir_path+'/win10/kmclassdll.dll')
kmclass_driver_path = os.path.abspath(driver_dir_path+'/kmclass.sys').encode(encoding='utf-8')

class DriverKey():
    def __init__(self) :
        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True
        self.load_driver()
        self.start()

    def start(self):
        """Starts this DriverKey's thread."""

        print('\n[~] Started DriverKey')
        self.thread.start()

    def _main(self):
        self.key_down_queue = []
        self.key_up_queue = []
        while(True):
            for k in self.key_up_queue:
                self._key_up(k)
                self.key_up_queue.remove(k)
            for k in self.key_down_queue:
                self._key_down(k)
            sleep(0.03)

    def user_key_down(self,key):
        if not key in self.key_down_queue:
            self.key_down_queue.append(key)

    def user_key_up(self,key):
        if key in self.key_down_queue:
            self.key_down_queue.remove(key)
        self.key_up_queue.append(key)

    def _key_up(self,key): 
        except_keys = [0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x2D,0x2E]
        if key in except_keys:
            self._key_up_e1(key)
        else:
            self.driver.KeyUp(key)

    def _key_down(self,key):
        except_keys = [0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x2D,0x2E]
        if key in except_keys:
            self._key_down_e0(key)
        else:
            self.driver.KeyDown(key)

    def _key_up_e1(self,key): 
        self.driver.KeyUpE1(key)

    def _key_down_e0(self,key):
        self.driver.KeyDownE0(key)

    def _left_button_down(self):
        self.driver.MouseLeftButtonDown()

    def _left_button_up(self):
        self.driver.MouseLeftButtonUp()

    def _right_button_down(self):
        self.driver.MouseRightButtonDown()

    def _right_button_up(self):
        self.driver.MouseRightButtonUp()

    def _middle_button_down(self):
        self.driver.MouseMiddleButtonDown()

    def _middle_button_up(self):
        self.driver.MouseMiddleButtonUp()

    def _move_rel(self,x, y):
        self.driver.MouseMoveRELATIVE(x,y)

    def _move_to(self,x, y):
        self.driver.MouseMoveABSOLUTE(x,y)

    def load_driver(self):
        self.driver = CDLL(kmclass_dll_path)
        self.driver.LoadNTDriver('kmclass',kmclass_driver_path)
        self.driver.SetHandle()

    def unload_driver(self):
        self.driver.UnloadNTDriver('kmclass')

