# -*- coding: utf-8 -*-
from src.common import utils, config
import cv2

class WorldMap():
    # check_image dir 
    MAP_CHECK_DIR = 'assets/map_check'
    MAP_OPEN_PNG = cv2.imread('assets/world_map_open.png', 0)
    MENU_GAP = 16

    def __init__(self):
        # standard point
        self.standard_point = (235,170)
        self.refresh_standard_point()
        
        # fixed points
        self.WORLD_MENU = self.get_final_pos(115,15)
        self.AREA_MENU = self.get_final_pos(250,15)
        self.SEARCH_BAR = self.get_final_pos(700,15)
        self.SEARCH_BTN = self.get_final_pos(765,15)
        self.FIRST_RESULT = self.get_final_pos(715,55)
        self.MAP_CHECK_LT = self.get_final_pos(47,16)
        self.MAP_CHECK_BR = self.get_final_pos(200,48)

        # worlds
        self.MAPLE_WORLD_PONINT = self.get_final_pos(60,31)
        self.GRANDIS_PONINT = self.get_final_pos(60,31+self.MENU_GAP*1)
        self.ARCANE_RIVER_PONINT = self.get_final_pos(60,31+self.MENU_GAP*2)

        # areas - arcane river
        self.VANISHING_JOURNEY = self.get_final_pos(185,47)
        self.REVERSE_CITY = self.get_final_pos(185,47+self.MENU_GAP*1)
        self.CHU_CHU_ISLAND = self.get_final_pos(185,47+self.MENU_GAP*2)
        self.YUM_YUM_ISLAND = self.get_final_pos(185,47+self.MENU_GAP*3)
        self.LACHELEIN = self.get_final_pos(185,47+self.MENU_GAP*4)
        self.ARCANA = self.get_final_pos(185,47+self.MENU_GAP*5)
        self.MORASS = self.get_final_pos(185,47+self.MENU_GAP*6)
        self.ESFERA = self.get_final_pos(185,47+self.MENU_GAP*7)
        self.SELLAS = self.get_final_pos(185,47+self.MENU_GAP*8)
        self.TENEBRIS = self.get_final_pos(185,47+self.MENU_GAP*9)
        self.MOONBRIDGE = self.get_final_pos(185,47+self.MENU_GAP*10)
        self.SUFFERING = self.get_final_pos(185,47+self.MENU_GAP*11)
        self.LIMINA = self.get_final_pos(185,47+self.MENU_GAP*12)

        self.maps_info = {
            "鏡光大海3" : {
                'map_name' : '鏡光大海3',
                'check_image' : self.MAP_CHECK_DIR + '/mirror_touched_sea3.png',
                'world_selection_point':self.ARCANE_RIVER_PONINT,
                'area_selection_point':self.ESFERA,
                'point':self.get_final_pos(487,430)
            },
            "鏡光大海2" : {
                'map_name' : '鏡光大海2',
                'check_image' : self.MAP_CHECK_DIR + '/mirror_touched_sea2.png',
                'world_selection_point':self.ARCANE_RIVER_PONINT,
                'area_selection_point':self.ESFERA,
                'point':self.get_final_pos(416,394)
            },
            "五道洞穴的上路" : {
                'map_name' : '五道洞穴的上路',
                'check_image' : self.MAP_CHECK_DIR + '/five_road_upper_path.png',
                'world_selection_point':self.ARCANE_RIVER_PONINT,
                'area_selection_point':self.ARCANA,
                'point':self.get_final_pos(256,455)
            },
        }

    def refresh_standard_point(self):
        frame = config.capture.frame
        point = utils.multi_match(frame, self.MAP_OPEN_PNG, threshold=0.9)
        if len(point) > 0:
            print("world map opened")
            self.standard_point = (point[0][0]-431,point[0][1]-10)
            return self.standard_point
        else:
            return False

    def get_final_pos(self,x,y):
        return (lambda x : (self.standard_point[0]+x[0],self.standard_point[1]+x[1]))((x,y))

    def check_if_in_correct_map(self,map_name):
        if map_name in self.maps_info:
            frame = config.capture.frame
            frame = frame[10:57, 10:234]
            template = cv2.imread(self.maps_info[map_name]['check_image'], 0)
            point = utils.multi_match(frame, template, threshold=0.9)
            if len(point) > 0:
                print("in correct map")
                return True
        return False
