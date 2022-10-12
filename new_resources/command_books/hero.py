"""A collection of all commands that Adele can use to interact with the game. 	"""

from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up

### image dir
IMAGE_DIR = config.RESOURCES_DIR + '/command_books/hero/'
# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    FLASH_JUMP = 'alt'
    UP_JUMP = 'shift'
    ROPE = 'c'
    # Buffs

    # Buffs Toggle

    # Attack Skills
    SKILL_Q = 'q' # 烈焰翔斬
    SKILL_1 = '1' # 狂暴攻擊
    SKILL_2 = '2' # 憤怒爆發
    SKILL_3 = '3' # 靈氣之刃
    SKILL_W = 'w' # 空間斬
    SKILL_A = 'a' # 劍之幻象
    SKILL_X = 'x' # 閃光斬

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
            # if abs(d_x) > 25:
            #     time.sleep(utils.rand_float(0.05, 0.08))
            #     press(Key.FLASH_JUMP, 1,up_time=0.08)
            time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.SKILL_1,1)
            time.sleep(utils.rand_float(0.45, 0.55))
            utils.wait_for_is_standing(200)
    
    if direction == 'up':
        utils.wait_for_is_standing(500)
        if abs(d_y) > 6 :
            if abs(d_y) > 23:
                press(Key.JUMP, 1)
                time.sleep(utils.rand_float(0.1, 0.15))
            press(Key.ROPE, 1)
            time.sleep(utils.rand_float(1.2, 1.5))
            utils.wait_for_is_standing(300)
        else:
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.1, 0.15))
    if direction == 'down':
        time.sleep(utils.rand_float(0.05, 0.07))
        press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.1, 0.15))
        # if d_x > 0:
        #     key_up("down")
        #     time.sleep(utils.rand_float(0.07, 0.1))
        #     key_down("right")
        #     time.sleep(utils.rand_float(0.07, 0.1))
        #     press(Key.JUMP,1)
        #     key_up("right")
        # elif d_x < 0:
        #     key_up("down")
        #     time.sleep(utils.rand_float(0.07, 0.1))
        #     key_down("left")
        #     time.sleep(utils.rand_float(0.07, 0.1))
        #     press(Key.JUMP,1)
        #     key_up("left")
        utils.wait_for_is_standing(100)
      

class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)

    def main(self):
        counter = self.max_steps
        toggle = True
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
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
            error = utils.distance(config.player_pos, self.target)
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
        time.sleep(utils.rand_float(0.04, 0.06))
        press(Key.JUMP, 1,up_time=0.1)
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1,up_time=0.05)
            if self.triple_jump:
                time.sleep(utils.rand_float(0.05, 0.08))
                press(Key.FLASH_JUMP, 1,up_time=0.05) # if this job can do triple jump
        key_up(self.direction)
        time.sleep(utils.rand_float(0.05, 0.08))
			

class UpJump(Command):
    """Performs a up jump in the given direction."""
    _display_name = '上跳'

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)

    def main(self):
        utils.wait_for_is_standing(2000)
        key_down(self.direction)
        time.sleep(utils.rand_float(0.03, 0.05))
        press(Key.UP_JUMP, 1)
        key_up(self.direction)
        time.sleep(utils.rand_float(0.4, 0.6))

class Rope(Command):
    """Performs a up jump in the given direction."""
    _display_name = '連接繩索'

    def __init__(self, jump = 'false'):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            utils.wait_for_is_standing(2000)
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.03, 0.05))
        press(Key.ROPE, 1, up_time=0.1)
        time.sleep(utils.rand_float(1.2, 1.4))

# 烈焰翔斬
class Skill_Q(Command):
    """Attacks using '烈焰翔斬' in a given direction."""
    _display_name = '烈焰翔斬'

    def __init__(self, direction,jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump and not utils.check_is_jumping():
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.JUMP, 1)
        else:
            key_down(self.direction)
        time.sleep(utils.rand_float(0.03, 0.05))
        press(Key.SKILL_Q, 1, up_time=0.1)
        # if config.stage_fright and utils.bernoulli(0.7):
        #     time.sleep(utils.rand_float(0.1, 0.2))
        key_up(self.direction)
        time.sleep(utils.rand_float(0.5, 0.65))

# 狂暴攻擊
class Skill_1(Command):
    """Attacks using '狂暴攻擊' in a given direction."""
    _display_name = '狂暴攻擊'

    def __init__(self, direction='left',jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump and not utils.check_is_jumping():
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.JUMP, 1)
        else:
            key_down(self.direction)
        time.sleep(utils.rand_float(0.03, 0.05))
        press(Key.SKILL_1, 1, up_time=0.1)
        # if config.stage_fright and utils.bernoulli(0.7):
        #     time.sleep(utils.rand_float(0.1, 0.2))
        key_up(self.direction)
        time.sleep(utils.rand_float(0.4, 0.55))

# 憤怒爆發
class Skill_2(Command):
    """Attacks using '憤怒爆發' in a given direction."""
    _display_name = '憤怒爆發'
    skill_cool_down = 10

    def __init__(self, direction='left'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.SKILL_2, 1, up_time=0.1)
            # if config.stage_fright and utils.bernoulli(0.7):
            #     time.sleep(utils.rand_float(0.1, 0.2))
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.7, 0.8))

# 靈氣之刃
class Skill_3(Command):
    """Attacks using '靈氣之刃' in a given direction."""
    _display_name = '靈氣之刃'
    skill_cool_down = 7

    def __init__(self, direction='left',jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(2000)
                key_down(self.direction)
                time.sleep(utils.rand_float(0.03, 0.05))
                press(Key.JUMP, 1)
            else:
                key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.SKILL_3, 1, up_time=0.1)
            # if config.stage_fright and utils.bernoulli(0.7):
            #     time.sleep(utils.rand_float(0.1, 0.2))
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.44, 0.55))

# 空間斬
class Skill_W(Command):
    """Attacks using '空間斬' in a given direction."""
    _display_name = '空間斬'
    skill_cool_down = 20

    def __init__(self):
        super().__init__(locals())

    def main(self):
        if self.check_is_skill_ready():
            press(Key.SKILL_W, 1, up_time=0.1)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(1.5, 1.7))

# 劍之幻象
class Skill_A(Command):
    """Attacks using '劍之幻象' in a given direction."""
    _display_name = '劍之幻象'
    skill_cool_down = 30

    def __init__(self, direction='left',jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(2000)
                key_down(self.direction)
                time.sleep(utils.rand_float(0.03, 0.05))
                press(Key.JUMP, 1)
            else:
                key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.SKILL_A, 1, up_time=0.1)
            # if config.stage_fright and utils.bernoulli(0.7):
            #     time.sleep(utils.rand_float(0.1, 0.2))
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.5, 0.6))

# 閃光斬
class Skill_X(Command):
    """Attacks using '閃光斬' in a given direction."""
    _display_name = '閃光斬'
    skill_cool_down = 7

    def __init__(self, direction='left',jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(2000)
                key_down(self.direction)
                time.sleep(utils.rand_float(0.03, 0.05))
                press(Key.JUMP, 1)
            else:
                key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.05))
            press(Key.SKILL_X, 1, up_time=0.1)
            # if config.stage_fright and utils.bernoulli(0.7):
            #     time.sleep(utils.rand_float(0.1, 0.2))
            key_up(self.direction)
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(0.4, 0.52))