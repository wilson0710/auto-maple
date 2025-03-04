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
    UPJUMP = 'space' # 上跳

    # Buffs
    BUFF_HOME = 'home' # 召喚冰魔
    BUFF_1 = '1' # 召喚冰魔
    BUFF_2 = '2' # 召喚冰魔
    BUFF_3 = '3' # 召喚冰魔
    BUFF_4 = '4' # 召喚冰魔
    BUFF_5 = '5' # 召喚冰魔
    BUFF_6 = '6' # 召喚冰魔
    BUFF_7 = '7' # 召喚冰魔
    # Buffs Toggle

    # Attack Skills
    SKILL_C = 'c'
    SKILL_3 = '3'
    SKILL_4 = '4'
    SKILL_Q = 'q'
    SKILL_C = 'c'
    SKILL_F = 'f'




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

    # if not check_current_tag('alpha'):
    #     utils.wait_for_is_standing(1000)
    #     Skill_A().execute()
    if config.player_states['is_stuck'] and abs(d_x) >= 17:
        print("is stuck")
        time.sleep(utils.rand_float(0.2, 0.3))
        press(Key.JUMP)
        WaitStanding(duration='1').execute()
        # if d_x <= 0:
        #     Fall(direction='left',duration='0.3')
        # else:
        #     Fall(direction='right',duration='0.3')
        config.player_states['is_stuck'] = False
    if direction == 'left' or direction == 'right':
        if abs(d_x) >= 17:
            Teleport(direction='',combo='true').execute()
            Skill_A(combo='true').execute()
        elif abs(d_x) > 10:
            time.sleep(utils.rand_float(0.25, 0.35))
        else:
            time.sleep(utils.rand_float(0.01, 0.015))
        utils.wait_for_is_standing(200)
        # d_x = target[0] - config.player_pos[0]
        # if abs(d_x) >= settings.move_tolerance and config.player_states['in_bottom_platform'] == False and len(settings.platforms) > 0:
        #     print('back to ground')
        #     key_up(direction)
        #     time.sleep(utils.rand_float(0.3, 0.4))
        #     Fall(duration='0.2').execute()
        #     Teleport(direction='down').execute()
        #     Skill_A(combo='True').execute()
    
    if direction == 'up':
        if abs(d_x) <= settings.move_tolerance and not config.player_states['is_keydown_skill']:
            time.sleep(utils.rand_float(0.2, 0.25))
            key_up('left')
            key_up('right')
            if abs(d_y) > 3 :
                if abs(d_y) >= 40:
                    UpJump().execute()
                    Teleport(direction=direction,jump='false',combo='true').execute()
                elif abs(d_y) >= 25:
                    Teleport(direction=direction,jump='true',combo='true').execute()
                else:
                    Teleport(direction=direction).execute()
                utils.wait_for_is_standing(300)
                Skill_A(combo='False').execute()
            else:
                press(Key.JUMP, 1)
                time.sleep(utils.rand_float(0.2, 0.25))
    if direction == 'down':
        if abs(d_x) <= settings.move_tolerance:
            key_up('left')
            key_up('right')
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
                print("down stair")
                if abs(d_y) >= 25 :
                    time.sleep(utils.rand_float(0.2, 0.3))
                    Fall(duration='0.3').execute()
                if abs(d_y) > 10 and utils.bernoulli(0.9):
                    Teleport(direction=direction,combo='true').execute()
                    Skill_A(combo='True').execute()
                else:
                    time.sleep(utils.rand_float(0.2, 0.3))
                    Fall(duration='0.3').execute()
        time.sleep(utils.rand_float(0.05, 0.08))
        utils.wait_for_is_standing(800)

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

class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = 'Up Jump'

    def __init__(self, direction="", jump='False',combo="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        self.player_jump(self.direction)
        time.sleep(utils.rand_float(0.03, 0.06)) 
        press(Key.UPJUMP, 1,up_time=0.05)
        key_up(self.direction)
        if self.combo:
            time.sleep(utils.rand_float(0.05, 0.1))
        else:
            time.sleep(utils.rand_float(0.4, 0.6))

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
        Teleport(direction=self.direction,combo="true",jump=str(self.jump)).execute()
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
    skill_cool_down=0
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
