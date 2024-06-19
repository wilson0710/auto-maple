from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, Frenzy, Player_jump, WaitStanding, WealthPotion
from src.common.vkeys import press, key_down, key_up
import cv2

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/buccaneer/'

LOTD_BUFF_TEMPLATE = cv2.imread(IMAGE_DIR + 'lotd.png', 0)
DEATH_DEBUFF_TEMPLATE = cv2.imread(IMAGE_DIR + 'dp_template.png', 0)
CHARM_TEMPLATE = cv2.imread(IMAGE_DIR + 'charm_template.png', 0)
CASH_TAB_TEMPLATE = cv2.imread(IMAGE_DIR + 'cashtab_template.png', 0)

# List of key mappings
class Key:
    # Movement
    JUMP = 'space'
    FLASH_JUMP = 'space'
    ROPE = 'ctrl'
    UP_JUMP = 'up+space'
    DOWN_JUMP = 'down+space'
    ADVANCED_DASH = 'shift'

    # Buffs
    BUFF_1          = '1'    # 
    BUFF_HOME       = 'home' # 
    BUFF_5          = '5'    # 
    BUFF_6          = '6'    #
    BUFF_7          = '7'    # 
    BUFF_8          = '8'    # 
    BUFF_9          = '9'    # Speed Infusion
    BUFF_0          = '0'    # Maple Warrior


    # Potion
    GOLD_POT = '.'          #MPARK GOLD POT
    EXP_15M = ';'
    
    # Attack Skills
    SKILL_G = 'g'           #LOTD
    SKILL_D = 'd'           #Serpent Vortex
    SKILL_X = 'x'           #Hook Bomber
    SKILL_F = 'down+f'      #Erda Shower
    SKILL_A = 'a'           #True Arachnid Reflection
    SKILL_S = 's'           #Corkscrew Blow
    SKILL_R = 'r'           #Howling Fist

    # special Skills
    # SP_F12 = 'f12'      # 輪迴

def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]

    if direction == 'left' or direction == 'right':
        utils.wait_for_is_standing(1000)
        d_y = target[1] - config.player_pos[1]
        d_x = target[0] - config.player_pos[0]
        if config.player_states['is_stuck'] and abs(d_x) < 16:
            print("is stuck")
            time.sleep(utils.rand_float(0.1, 0.2))
            press(Key.JUMP)
            Skill_X(direction='').execute()
            WaitStanding(duration='1').execute()
        if abs(d_x) >= 16:
            if abs(d_x) >= 60:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            elif abs(d_x) >= 28:
                FlashJump(direction='',triple_jump='false',fast_jump='false').execute()
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            else:
                if d_y == 0:
                    Skill_S().execute()
                else:
                    Skill_X(direction='',jump='true').execute()
            time.sleep(utils.rand_float(0.04, 0.06))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            utils.wait_for_is_standing(500)
        else:
            time.sleep(utils.rand_float(0.05, 0.08))
            utils.wait_for_is_standing(500)
    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_x) > settings.move_tolerance:
            return
        if abs(d_y) > 6 :
            if abs(d_y) > 36:
                press(Key.JUMP, 1)
                time.sleep(utils.rand_float(0.1, 0.15))
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
            elif abs(d_y) <= 25:
                UpJump().execute()
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
                SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
            utils.wait_for_is_standing(300)
        else:
            press(Key.JUMP, 1) 
            time.sleep(utils.rand_float(0.1, 0.15))

    if direction == 'down':
        if abs(d_x) > settings.move_tolerance:
            return
        down_duration = 0.15                #changed
        if abs(d_y) > 20:
            down_duration = 0.55            #changed
        elif abs(d_y) > 13:
            down_duration = 0.35            #changed
        
        if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
            # print("down stair")
            if abs(d_x) >= 5:
                if d_x > 0:
                    Fall(direction='right',duration=down_duration).execute()
                else:
                    Fall(direction='left',duration=down_duration).execute()
                
            else:
                Fall(direction='',duration=(down_duration+0.1)).execute()
                if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING:
                    print("leave lader")
                    if d_x > 0:
                        key_down('left')
                        press(Key.JUMP)
                        key_up('left')
                    else:
                        key_down('right')
                        press(Key.JUMP)
                        key_up('right')
            SkillCombination(direction='',jump='false',target_skills='skill_x').execute()
                
        utils.wait_for_is_standing(2000)
        time.sleep(utils.rand_float(0.1, 0.12))

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        threshold = settings.adjust_tolerance
        d_x = self.target[0] - config.player_pos[0]
        d_y = self.target[1] - config.player_pos[1]
        while config.enabled and counter > 0 and (abs(d_x) > threshold or abs(d_y) > threshold):
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.01, 0.02))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.01, 0.02))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance:
                    if d_y < 0:
                        utils.wait_for_is_standing(1000)
                        UpJump().main()                                         #changed
                    else:
                        utils.wait_for_is_standing(1000)
                        key_down('down')
                        time.sleep(utils.rand_float(0.05, 0.07))
                        press(Key.JUMP, 1, down_time=0.1)                       #changed
                        key_up('down')
                        time.sleep(utils.rand_float(0.17, 0.25))
                    counter -= 1
            d_x = self.target[0] - config.player_pos[0]
            d_y = self.target[1] - config.player_pos[1]
            toggle = not toggle

class Buff(Command):
    """Uses each of Adele's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd120_buff_time = 0
        self.cd150_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        # buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL, Key.SHARP_EYE, Key.COMBAT_ORDERS, Key.ADVANCED_BLESSING]
        buffs = [Key.BUFF_HOME, Key.BUFF_5, Key.BUFF_6, Key.BUFF_7, Key.BUFF_8, Key.BUFF_9, Key.BUFF_0]
        now = time.time()
        utils.wait_for_is_standing(1000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 121:
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd150_buff_time > 151:
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            # Skill_4().execute()
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            self.cd900_buff_time = now
        if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
	        for key in buffs:
		        press(key, 2, up_time=0.3)
	        self.decent_buff_time = now		

class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = 'Flash Jump'

    def __init__(self, direction="",jump='false',combo='False',triple_jump="False",fast_jump="false",reverse_triple='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)
        self.jump = settings.validate_boolean(jump)
        self.reverse_triple = settings.validate_boolean(reverse_triple)

    def main(self):
        if not self.jump:
            utils.wait_for_is_standing()
            if not self.fast_jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.04)) # fast flash jump gap
            else:
                key_down(self.direction,down_time=0.05)
                press(Key.JUMP,down_time=0.06,up_time=0.05)
        else:
            key_down(self.direction,down_time=0.05)
            press(Key.JUMP,down_time=0.06,up_time=0.05)
        
        press(Key.FLASH_JUMP, 1,down_time=0.06,up_time=0.01)
        key_up(self.direction,up_time=0.01)
        if self.triple_jump:
            time.sleep(utils.rand_float(0.03, 0.05))
            # reverse_direction
            reverse_direction = ''
            if self.reverse_triple:
                if self.direction == 'left':
                    reverse_direction = 'right'
                elif self.direction == 'right':
                    reverse_direction = 'left'
                print('reverse_direction : ',reverse_direction)
                key_down(reverse_direction,down_time=0.05)
            else:
                time.sleep(utils.rand_float(0.02, 0.03))
            press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
            if self.reverse_triple:
                key_up(reverse_direction,up_time=0.01)
        time.sleep(0.8)
        time.sleep(utils.rand_float(0.01, 0.02))

class CheckDeathPenalty(Command):
    _display_name ='Check Death Penalty'

    def main(self):

        frame = config.capture.frame

        # check for debuff
        death_debuff = utils.multi_match(frame[:95, :], DEATH_DEBUFF_TEMPLATE,threshold=0.93)
        
        if len(death_debuff) > 0 :

            #Open inventory
            press("i")

            #capture frame with invent opened
            frame = config.capture.frame

            #Check if cash tab is cuurently selected
            cash_tab_icon = utils.multi_match(frame[:, :], CASH_TAB_TEMPLATE,threshold = 0.93)
            if len(cash_tab_icon) > 0 :
                cash_tab_pos = min(cash_tab_icon, key=lambda p: p[0])
                target = (round(cash_tab_pos[0]), round(cash_tab_pos[1]))
                utils.game_window_click(target, button='left', click_time = 1, delay = 0.01)

            #ADJUST this if u get a noti saying you are in combat and you cant use item
            time.sleep(0.2)

            #Recapture a new frame with charm in the picture
            frame = config.capture.frame

            #Check for safety charm
            charm_icon = utils.multi_match(frame[:, :], CHARM_TEMPLATE,threshold = 0.93)

            #Use charm
            if len(charm_icon) > 0 :
                charm_pos = min(charm_icon, key=lambda p: p[0])
                target = (round(charm_pos[0]), round(charm_pos[1]))
                utils.game_window_click(target, button='left', click_time = 2, delay = 0.01)
            else:
                print("No charm in inventory!")

            #Close inventory
            press("i")

        #else:
            #No death debuff effects
            #print("no debuff effect")

class UpJump(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = 'Up Jump'
    _distance = 27
    key=Key.UP_JUMP
    delay=0.1
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1
    def main(self):
        self.jump = True
        super().main()
        
class Rope(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = 'Rope Lift'
    _distance = 27
    key=Key.ROPE
    delay=1.4
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.2

class SuperJump(Command):
    """Performs a super jump in the given direction."""

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        key_down(self.direction)
        time.sleep(0.1)
        key_down(Key.ADVANCED_DASH,0)
        key_down(Key.JUMP,0)
        time.sleep(0.125)
        key_up(Key.ADVANCED_DASH,0)
        key_up(Key.JUMP)
        key_up(self.direction,0)
        time.sleep(0.5)

class CheckLOTD(Command):
    _display_name ='Check LOTD'

    def main(self):
        frame = config.capture.frame
        # check for buff
        lotd_buff = utils.multi_match(frame[:, :], LOTD_BUFF_TEMPLATE,threshold=0.93)
        if len(lotd_buff) <= 0 :
            Skill_G().execute()

class FaceLeft(BaseSkill):
    """Performs a flash jump in the given direction."""
    _display_name = 'FaceLeft'
    _distance = 1
    key='left'
    delay=0.1
    rep_interval=0
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.0

class FaceRight(BaseSkill):
    """Performs a flash jump in the given direction."""
    _display_name = 'FaceRight'
    _distance = 1
    key='right'
    delay=0.1
    rep_interval=0
    skill_cool_down=0
    ground_skill=False
    buff_time=0

class FJMobbing(Command):
    """Performs a flash jump in the given direction."""
    _display_name = 'FJMobbing'
    
    def __init__(self, direction=""):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        if self.direction == 'left':
            FaceLeft().execute()
        if self.direction == 'right':
            FaceRight().execute()

        press(Key.JUMP,down_time=0.04,up_time=0.02)
        press(Key.FLASH_JUMP, 1,down_time=0.06,up_time=0.05)
        Skill_X().execute()
        time.sleep(0.3)

class FJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = 'FJump'
    
    def __init__(self, direction=""):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        press(Key.JUMP,down_time=0.04,up_time=0.02)
        press(Key.FLASH_JUMP, 1,down_time=0.06,up_time=0.05)
        time.sleep(1.0)



class Gold_Pot(BaseSkill):
    _display_name ='MP Gold Pot'
    key=Key.GOLD_POT
    delay=0.5
    rep_interval=0.5
    skill_cool_down=1800
    ground_skill=False
    buff_time=1800
    combo_delay = 0.2

class EXP_15M(BaseSkill):
    _display_name ='15 Min EXP'
    key=Key.EXP_15M
    delay=0.5
    rep_interval=0.5
    skill_cool_down=900
    ground_skill=False
    buff_time=900
    combo_delay = 0.2

class Skill_G(BaseSkill):
    _display_name ='Lord of the Deep'
    key=Key.SKILL_G
    delay=0.5
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=60
    combo_delay = 0.2
    skill_image = IMAGE_DIR + 'lotd.png'


class Skill_D(BaseSkill):
    _display_name ='Serpent Vortex'
    key=Key.SKILL_D
    delay=0.3
    rep_interval=0.25
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

class Skill_F(BaseSkill):
    _display_name ='Erda Shower'
    key=Key.SKILL_F
    delay=0.9
    rep_interval=0.25
    skill_cool_down=57
    ground_skill=True
    buff_time=60
    combo_delay = 0.3

class Skill_X(BaseSkill):
    _display_name = 'Hook Bomber'
    _distance = 27
    key=Key.SKILL_X
    delay=0.45
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.25

class Skill_A(BaseSkill):
    _display_name ='True Arachnid Reflection'
    key=Key.SKILL_A
    delay=0.6
    rep_interval=0.25
    skill_cool_down=240
    ground_skill=False
    buff_time=0
    combo_delay = 0.4

class Skill_S(BaseSkill):
    _display_name ='Corkscrew Blow'
    key=Key.SKILL_S
    delay=0.5
    rep_interval=0.25
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.3

    
class Skill_R(BaseSkill):
    _display_name ='Howling Fist'
    key=Key.SKILL_R
    delay=0.9
    rep_interval=0.25
    skill_cool_down=90
    ground_skill=False
    buff_time=90
    combo_delay = 0.3
    

class AutoHunting(Command):
    _display_name ='Auto Hunting'

    def __init__(self,duration='180',map=''):
        super().__init__(locals())
        self.duration = float(duration)
        self.map = map

    def main(self):
        daily_complete_template = cv2.imread('assets/daily_complete.png', 0)
        start_time = time.time()
        toggle = True
        move = config.bot.command_book['move']
        GoToMap(target_map=self.map).execute()
        SkillCombination(direction='',target_skills='skill_x').execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                Skill_X().execute()
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_X().execute()
                continue
            Frenzy().execute()
            frame = config.capture.frame
            point = utils.single_match_with_threshold(frame,daily_complete_template,0.9)
            if len(point) > 0:
                print("one daily end")
                break
            minimap = config.capture.minimap['minimap']
            height, width, _n = minimap.shape
            if time.time() - start_time >= self.duration:
                break
            if not config.enabled:
                break
            
            if toggle:
                # right side
                move((width-20),bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='left').execute()
                Skill_D(direction='left+up').execute()
                Skill_S().execute()
                FlashJump(direction='left').execute()
                SkillCombination(direction='left',target_skills='skill_x').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                if config.player_pos[1] >= bottom_y:
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                FlashJump(direction='right').execute()
                Skill_D(direction='right+up').execute()
                Skill_S().execute()
                FlashJump(direction='right').execute()
                SkillCombination(direction='right',target_skills='skill_x').execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                Skill_X().execute()
                continue
            move(width//2,bottom_y).execute()
            UpJump(jump='true').execute()
            SkillCombination(direction='left',target_skills='skill_x').execute()
            SkillCombination(direction='right',target_skills='skill_x').execute()
            toggle = not toggle
            

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
