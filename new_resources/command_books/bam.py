from src.common import config, settings, utils
import time
import cv2
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill, GoToMap, ChangeChannel, WaitStanding
from src.common.vkeys import press, key_down, key_up

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/bam/'

# List of key mappings
class Key:
    # Movement
    JUMP = 'space'
    TELEPORT = 'shift' # 瞬移
    UPJUMP = 'up+space' # 上跳
    ROPE = 'ctrl'


    # Buffs
    BUFF_HOME = 'home' # 召喚冰魔
    BUFF_1 = '1' # 召喚冰魔
    BUFF_2 = '2' # 召喚冰魔
    BUFF_3 = '3' # 召喚冰魔
    BUFF_4 = '4' # 召喚冰魔
    BUFF_5 = '5' # 召喚冰魔
    BUFF_6 = '6' # 召喚冰魔
    BUFF_7 = '7' # 召喚冰魔
    BUFF_8 = '8' # 召喚冰魔
    BUFF_9 = '9' # 召喚冰魔
    BUFF_0 = '0' # 召喚冰魔
    # Buffs Toggle

    # Attack Skills
    SKILL_C = 'c'
    SKILL_3 = '3'
    SKILL_3DOWN = 'down+3'
    SKILL_4 = '4'
    SKILL_Q = 'q'
    SKILL_C = 'c'
    SKILL_F = 'f'
    SKILL_X = 'x'




    # special Skills
    SP_F12 = 'f12' # 輪迴
    CTRL = 'ctrl'

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
            WaitStanding(duration='1').execute()
        if abs(d_x) >= 16:
            if abs(d_x) >= 60:
                Teleport(direction='',combo='false').execute()
            elif abs(d_x) >= 28:
                Teleport(direction='',combo='false').execute()
            else:
                if d_y == 0:
                    Skill_X().execute()
            time.sleep(utils.rand_float(0.04, 0.06))
            # if abs(d_x) <= 22:
            #     key_up(direction)
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
                SkillCombination(direction='',jump='false',target_skills='skill_c').execute()
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
                SkillCombination(direction='',jump='false',target_skills='skill_c').execute()
            else:
                press(Key.ROPE, 1)
                time.sleep(utils.rand_float(1.2, 1.5))
                SkillCombination(direction='',jump='false',target_skills='skill_c').execute()
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
            SkillCombination(direction='',jump='false',target_skills='skill_c').execute()
                
        utils.wait_for_is_standing(2000)
        time.sleep(utils.rand_float(0.1, 0.12))

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5,direction="",jump='false',combo='false'):
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
                threshold = settings.adjust_tolerance
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left',down_time=0.02)
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            walk_counter += 1
                            time.sleep(0.01)
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right',down_time=0.02)
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            walk_counter += 1
                            time.sleep(0.01)
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance:
                    if d_y < 0:
                        Teleport(direction='up').execute()
                    else:
                        Fall(duration=0.2).execute()
                        time.sleep(utils.rand_float(0.05, 0.1))
                    counter -= 1
            d_x = self.target[0] - config.player_pos[0]
            d_y = self.target[1] - config.player_pos[1]
            toggle = not toggle

class Buff(Command):
    """Uses each of Adele's buffs once."""

    def __init__(self):
        super().__init__(locals())
        self.cd10_buff_time = 0
        self.cd120_buff_time = 0
        self.cd150_buff_time = 0
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        buffs = [Key.BUFF_HOME, Key.BUFF_7, Key.BUFF_8, Key.BUFF_9, Key.BUFF_0]
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

class Teleport(BaseSkill):
    _display_name ='Teleport'
    _distance = 17
    key=Key.TELEPORT
    delay=0.53
    rep_interval=0.3
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.15

class UpJump(BaseSkill):
    """Performs a up jump in the given direction."""
    _display_name = 'Up Jump'
    _distance = 27
    key=Key.UPJUMP
    delay=0.1
    rep_interval=0.5
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1
    def main(self):
        self.jump = True
        super().main()

class TeleportCombination(Command):
    """teleport with other skill."""
    _display_name = 'TP w Skill'

    def __init__(self, direction="left",combo_skill='',combo_direction='', jump='False',combo2="true"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo_skill = combo_skill.lower()
        self.combo2 = combo2
        self.combo_direction = settings.validate_arrows(combo_direction)

    def main(self):
        if not self.jump:
            utils.wait_for_is_standing()
        else:
            key_down(self.direction,down_time=0.05)
            press(Key.JUMP,down_time=0.02,up_time=0.02)

        skills_array = self.combo_skill.split("|")
        for skill in skills_array:
            skill = skill.lower()
            s = config.bot.command_book[skill]
            if not s.get_is_skill_ready():
                continue
            else:
                print(skill)
                s(direction=self.combo_direction,combo=self.combo2).execute()
                break
        Teleport(direction=self.direction,combo="true",jump='false').execute()
        
        

class Skill_X(BaseSkill):
    _display_name ='Battle Burst'
    key=Key.SKILL_X
    delay=0.54
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.24

class Skill_C(BaseSkill):
    _display_name ='Finishing Blow'
    key=Key.SKILL_C
    delay=0.54
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.24
    
class Skill_3(BaseSkill):
    _display_name ='Altar'
    key=Key.SKILL_3
    delay=0.54
    rep_interval=0.2
    skill_cool_down=40
    ground_skill=True
    buff_time=0
    combo_delay = 0.24

    
class Skill_3DOWN(BaseSkill):
    _display_name ='Altar Down'
    key=Key.SKILL_3DOWN
    delay=0.54
    rep_interval=0.2
    skill_cool_down=40
    ground_skill=True
    buff_time=0
    combo_delay = 0.24

class Skill_4(BaseSkill):
    _display_name ='Grim Harvest'
    key=Key.SKILL_4
    delay=0.54
    rep_interval=0.2
    skill_cool_down=90
    ground_skill=True
    buff_time=0
    combo_delay = 0.24

class Skill_F(BaseSkill):
    _display_name ='Erda Shower'
    key=Key.SKILL_F
    delay=0.54
    rep_interval=0.2
    skill_cool_down=60
    ground_skill=True
    buff_time=0
    combo_delay = 0.24

class Skill_Q(BaseSkill):
    _display_name ='Aura Scythe'
    key=Key.SKILL_Q
    delay=0.54
    rep_interval=0.2
    skill_cool_down=90
    ground_skill=True
    buff_time=0
    combo_delay = 0.24


class AutoHunting(Command):
    _display_name ='自動走位狩獵'

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
        Skill_D().execute()
        minimap = config.capture.minimap['minimap']
        height, width, _n = minimap.shape
        bottom_y = height - 30
        # bottom_y = config.player_pos[1]
        settings.platforms = 'b' + str(int(bottom_y))
        while True:
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                continue
            Sp_F12().execute()
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
                # Teleport(direction='down').execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                print("current player : ", str(config.player_pos[1]))
                time.sleep(0.2)
                TeleportCombination(direction='right',combo_skill='skill_q|skill_3|skill_s',combo_direction='left').execute()
                TeleportCombination(direction='left',combo_skill='skill_x',combo2='false').execute()
                UpJump(combo='true',direction='left').execute()
                TeleportCombination(direction='up',combo_skill='skill_x').execute()
            else:
                # left side
                move(20,bottom_y).execute()
                # Teleport(direction='down').execute()
                if config.player_pos[1] >= bottom_y:
                    print('new bottom')
                    bottom_y = config.player_pos[1]
                    settings.platforms = 'b' + str(int(bottom_y))
                print("current bottom : ", settings.platforms)
                time.sleep(0.2)
                TeleportCombination(direction='left',combo_skill='skill_q|skill_3|skill_s',combo_direction='right').execute()
                TeleportCombination(direction='right',combo_skill='skill_x',combo2='false').execute()
                UpJump(combo='true',direction='right').execute()
                TeleportCombination(direction='up',combo_skill='skill_x').execute()
            
            if settings.auto_change_channel and config.should_solve_rune:
                config.bot._solve_rune()
                continue
            if settings.auto_change_channel and config.should_change_channel:
                ChangeChannel(max_rand=40).execute()
                continue
            move(width//2,bottom_y).execute()
            time.sleep(0.35)
            SkillCombination(target_skills='skill_1|skill_w').execute()
            # TeleportCombination(direction='up',combo_skill='skill_x',jump='true').execute()
            toggle = not toggle
            

        if settings.home_scroll_key:
            config.map_changing = True
            press(settings.home_scroll_key)
            time.sleep(5)
            config.map_changing = False
        return
