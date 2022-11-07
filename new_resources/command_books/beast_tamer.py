"""A collection of all commands that Adele can use to interact with the game. 	"""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up

### image dir
IMAGE_DIR = config.RESOURCES_DIR + '/command_books/beast_tamer/'
# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    FLASH_JUMP = 'alt'
    UP_JUMP = 'c'

    # Buffs

    # Buffs Toggle

    # Attack Skills
    SKILL_A = 'a' # 隊伍攻擊
    SKILL_X = 'q' # 艾卡飛行
    SKILL_S = 's' # 隊伍轟炸
    
    


#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    num_presses = 2
    if direction == 'up' or direction == 'down':
        num_presses = 1
    # if config.stage_fright and direction != 'up' and utils.bernoulli(0.75):
    #     time.sleep(utils.rand_float(0.1, 0.3))
    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]
    
    if abs(d_x) > 15:
        if direction == 'left' or direction == 'right':
            press(Key.FLASH_JUMP, num_presses,up_time=0.08)
            if abs(d_x) > 25:
                time.sleep(utils.rand_float(0.05, 0.08))
                press(Key.FLASH_JUMP, 1,up_time=0.08)
            time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.SKILL_A,1)
            time.sleep(utils.rand_float(0.05, 0.08))
            utils.wait_for_is_standing(300)
    
    if direction == 'up':
        if abs(d_y) > 6 :
            if abs(d_y) > 23:
                press(Key.JUMP, 1)
                time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.UP_JUMP, 1)
            time.sleep(utils.rand_float(0.2, 0.3))
            utils.wait_for_is_standing(300)
        else:
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.1, 0.15))
    if direction == 'down':
        time.sleep(utils.rand_float(0.05, 0.07))
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.15, 0.25))
        utils.wait_for_is_standing(200)
      

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        d_x = self.target[0] - config.player_pos[0]
        d_y = self.target[1] - config.player_pos[1]
        while config.enabled and counter > 0 and (abs(d_x) > threshold or abs(d_y) > threshold):
            if toggle:
                d_x = self.target[0] - config.player_pos[0]
                # threshold = settings.adjust_tolerance / math.sqrt(2)
                threshold = settings.adjust_tolerance
                if abs(d_x) > threshold:
                    walk_counter = 0
                    if d_x < 0:
                        key_down('left')
                        while config.enabled and d_x < -1 * threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.04, 0.055))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('left')
                    else:
                        key_down('right')
                        while config.enabled and d_x > threshold and walk_counter < 60:
                            time.sleep(utils.rand_float(0.04, 0.055))
                            walk_counter += 1
                            d_x = self.target[0] - config.player_pos[0]
                        key_up('right')
                    counter -= 1
            else:
                d_y = self.target[1] - config.player_pos[1]
                if abs(d_y) > settings.adjust_tolerance:
                    if d_y < 0:
                        utils.wait_for_is_standing(1000)
                        UpJump('up').main()
                    else:
                        utils.wait_for_is_standing(1000)
                        key_down('down')
                        time.sleep(utils.rand_float(0.05, 0.07))
                        press(Key.JUMP, 2, down_time=0.1)
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
        self.cd180_buff_time = 0
        self.cd200_buff_time = 0
        self.cd240_buff_time = 0
        self.cd900_buff_time = 0
        self.decent_buff_time = 0

    def main(self):
        # buffs = [Key.SPEED_INFUSION, Key.HOLY_SYMBOL, Key.SHARP_EYE, Key.COMBAT_ORDERS, Key.ADVANCED_BLESSING]
        now = time.time()
        utils.wait_for_is_standing(2000)
        if self.cd120_buff_time == 0 or now - self.cd120_buff_time > 120:
            # press(Key.BUFF_1, 2)
            # time.sleep(utils.rand_float(0.6, 0.8))
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            # press(Key.BUFF_2, 2)
            # time.sleep(utils.rand_float(0.5, 0.7))
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now		


class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = '二段跳'

    def __init__(self, direction="left",triple_jump="False"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)

    def main(self):
        utils.wait_for_is_standing(2000)
        key_down(self.direction)
        time.sleep(utils.rand_float(0.03, 0.06))
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.05, 0.08)) # test flash jump gap
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1,up_time=0.05)
            if self.triple_jump:
                time.sleep(utils.rand_float(0.05, 0.08))
                press(Key.FLASH_JUMP, 1,up_time=0.05) # if this job can do triple jump
        key_up(self.direction)
        time.sleep(utils.rand_float(0.03, 0.05))
			

class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'

    def __init__(self, direction, jump='False',combo="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        utils.wait_for_is_standing(2000)
        key_down(self.direction)
        time.sleep(utils.rand_float(0.03, 0.05))
        if self.jump:
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.05, 0.07))
        press(Key.UP_JUMP, 1)
        press(Key.SKILL_4, 1) # eliminate delay of up_jump
        key_up(self.direction)
        if self.combo:
            time.sleep(utils.rand_float(0.05, 0.08))
        else:
            time.sleep(utils.rand_float(0.4, 0.6))

# 隊伍攻擊
class Skill_A(Command):
    """Attacks using '隊伍攻擊' in a given direction."""
    _display_name = '隊伍攻擊'

    def __init__(self, direction, attacks=2, repetitions=1,jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.JUMP, 1)
        else:
            key_down(self.direction)
        time.sleep(utils.rand_float(0.03, 0.05))
        for _ in range(self.repetitions):
            press(Key.SKILL_A, self.attacks, up_time=0.08)
        # if config.stage_fright and utils.bernoulli(0.7):
        #     time.sleep(utils.rand_float(0.1, 0.2))
        key_up(self.direction)
        if self.combo:
            if self.attacks == 3:
                time.sleep(utils.rand_float(0.1, 0.15))
            else:
                time.sleep(utils.rand_float(0.1, 0.15))
        else:
            if self.attacks == 3:
                time.sleep(utils.rand_float(0.35, 0.45))
            else:
                time.sleep(utils.rand_float(0.3, 0.35))

# 艾卡飛行
class Skill_X(Command):
    """Attacks using '艾卡飛行' in a given direction."""
    _display_name = '艾卡飛行'
    skill_cool_down = 60
    skill_image = IMAGE_DIR + 'skill_x.png'

    def __init__(self):
        super().__init__(locals())

    def main(self):
        if self.check_is_skill_ready():
            press(Key.SKILL_X, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            self.set_my_last_cooldown(time.time())
		
# 隊伍轟炸
class Skill_S(Command):
    """Attacks using '隊伍轟炸' in a given direction."""
    _display_name = '隊伍轟炸'
    skill_cool_down = 3
    skill_image = IMAGE_DIR + 'skill_s.png'

    def __init__(self):
        super().__init__(locals())

    def main(self):
        if self.check_is_skill_ready():
            press(Key.SKILL_S, 1)
            time.sleep(utils.rand_float(0.15, 0.2))
            self.set_my_last_cooldown(time.time())

