from src.common import config, settings, utils
import time
from src.routine.components import Command, CustomKey, SkillCombination, Fall, BaseSkill
from src.common.vkeys import press, key_down, key_up

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/ice_lightning/'

# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    TELEPORT = 'x' # 瞬移
    UPJUMP = 'c' # 上跳
    # Buffs
    BUFF_5 = '5' # 召喚冰魔
    # Buffs Toggle

    # Attack Skills
    SKILL_Q = 'q' # 落雷凝聚
    SKILL_S = 's'# 冰鋒刃
    SKILL_A = 'a' # 閃電連擊
    SKILL_D = 'd' # 閃電球
    SKILL_DD = 'down+d' # 放置閃電球
    SKILL_1 = '1' # 冰雪之精神
    SKILL_W = 'w' # 冰河紀元
    SKILL_E = 'e' # 暴風雪
    SKILL_F = 'f' # 
    SKILL_F1 = 'f1' # 魔力無限
    SKILL_F2 = 'f2' # 
    SKILL_2 = '2' # 
    SKILL_3 = '3' # 

    # special Skills
    SP_F12 = 'f12' # 輪迴

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

    if direction == 'left' or direction == 'right':
        if abs(d_x) >= 15:
            Teleport(direction=direction).execute()
            Skill_A(combo='True').execute()
        elif abs(d_x) > 10:
            time.sleep(utils.rand_float(0.1, 0.15))
        utils.wait_for_is_standing(200)
    
    if direction == 'up':
        if abs(d_y) > 3 :
            if abs(d_y) >= 40:
                UpJump().execute()
                Teleport(direction=direction,jump='true').execute()
            elif abs(d_y) >= 22:
                Teleport(direction=direction,jump='true').execute()
            else:
                Teleport(direction=direction).execute()
            utils.wait_for_is_standing(300)
        else:
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.1, 0.15))
    if direction == 'down':
        # if config.player_states['movement_state'] == config.MOVEMENT_STATE_STANDING and config.player_states['in_bottom_platform'] == False:
        print("down stair")
        if abs(d_y) > 8 :
            Teleport(direction=direction).execute()
        else:
            Fall().execute()
        time.sleep(utils.rand_float(0.05, 0.08))

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5,direction="",jump='false',combo='false'):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
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
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right',down_time=0.02)
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            walk_counter += 1
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
            error = utils.distance(config.player_pos, self.target)
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
        now = time.time()
        utils.wait_for_is_standing(1000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 121:
            # time.sleep(utils.rand_float(0.1, 0.2))
            # Skill_D().execute()
            self.cd120_buff_time = now
        if self.cd150_buff_time == 0 or now - self.cd150_buff_time > 151:
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            time.sleep(utils.rand_float(0.1, 0.2))
            press(Key.SKILL_F1, 1,up_time=0.3)
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            time.sleep(utils.rand_float(0.1, 0.2))
            press(Key.BUFF_5, 1,up_time=0.5)
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            # time.sleep(utils.rand_float(0.1, 0.3))
            # press(Key.BUFF_5, 1)
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now	

class Teleport(BaseSkill):
    _display_name ='瞬移'
    _distance = 27
    key=Key.TELEPORT
    delay=0.23
    rep_interval=0.3
    skill_cool_down=0
    ground_skill=False
    buff_time=0
    combo_delay = 0.1

class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'

    def __init__(self, direction="", jump='False',combo="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        self.player_jump(self.direction)
        time.sleep(utils.rand_float(0.03, 0.06)) 
        press(Key.UP_JUMP, 1,up_time=0.05)
        key_up(self.direction)
        if self.combo:
            time.sleep(utils.rand_float(0.1, 0.2))
        else:
            time.sleep(utils.rand_float(0.4, 0.6))

class Skill_A(BaseSkill):
    _display_name ='閃電連擊'
    key=Key.SKILL_A
    delay=0.48
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.08
    
class TeleportCombination(Command):
    """teleport with other skill."""
    _display_name = '瞬移組合'

    def __init__(self, direction="left",combo_skill='',combo_direction='', jump='False',combo2="true"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo_skill = combo_skill.lower()
        self.combo2 = combo2
        self.combo_direction = settings.validate_arrows(combo_direction)

    def main(self):
        Teleport(direction=self.direction,jump=str(self.jump)).execute()
        skills_array = self.combo_skill.split("|")
        for skill in skills_array:
            skill = skill.lower()
            s = config.bot.command_book[skill]
            if not s.get_is_skill_ready():
                continue
            else:
                s(direction=self.combo_direction,combo=self.combo2).execute()
                break

class Skill_S(BaseSkill):
    _display_name ='冰鋒刃'
    key=Key.SKILL_S
    delay=0.55
    rep_interval=0.2
    skill_cool_down=5
    ground_skill=True
    buff_time=0
    combo_delay = 0.15

class Skill_D(BaseSkill):
    _display_name ='閃電球'
    key=Key.SKILL_D
    delay=0.55
    rep_interval=0.2
    skill_cool_down=0
    ground_skill=True
    buff_time=120
    combo_delay = 0.15

class Skill_DD(BaseSkill):
    _display_name ='放置閃電球'
    key=Key.SKILL_DD
    delay=0.55
    rep_interval=0.2
    skill_cool_down=27
    ground_skill=True
    buff_time=50
    combo_delay = 0.2

class Skill_Q(BaseSkill):
    _display_name ='落雷凝聚'
    key=Key.SKILL_Q
    delay=0.4
    rep_interval=0.2
    skill_cool_down=39
    ground_skill=True
    buff_time=0
    combo_delay = 0.05
    skill_image = IMAGE_DIR + 'skill_q.png'

class Skill_W(BaseSkill):
    _display_name ='冰河紀元'
    key=Key.SKILL_W
    delay=0.55
    rep_interval=0.2
    skill_cool_down=58
    ground_skill=True
    buff_time=12
    combo_delay = 0.15
    skill_image = IMAGE_DIR + 'skill_w.png'

class Skill_E(BaseSkill):
    _display_name ='暴風雪'
    key=Key.SKILL_E
    delay=1
    rep_interval=0.2
    skill_cool_down=43
    ground_skill=True
    buff_time=0
    combo_delay = 1
    skill_image = IMAGE_DIR + 'skill_e.png'

class Skill_1(BaseSkill):
    _display_name ='冰雪之精神'
    key=Key.SKILL_1
    delay=0.48
    rep_interval=0.2
    skill_cool_down=114
    ground_skill=True
    buff_time=25
    combo_delay = 0.08
    skill_image = IMAGE_DIR + 'skill_1.png'

class Skill_3(BaseSkill):
    _display_name ='眾神之雷'
    key=Key.SKILL_3
    delay=0.52
    rep_interval=0.2
    skill_cool_down=114
    ground_skill=True
    buff_time=30
    combo_delay = 0.1
    skill_image = IMAGE_DIR + 'skill_3.png'

class Skill_F1(BaseSkill):
    _display_name ='魔力無限'
    key=Key.SKILL_F1
    delay=0.46
    rep_interval=0.2
    skill_cool_down=180
    ground_skill=True
    buff_time=69
    combo_delay = 0.1