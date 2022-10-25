from turtle import right
from sqlalchemy import true
from src.common import config, settings, utils
import time
import math
from src.routine.components import Command, CustomKey, SkillCombination, Fall
from src.common.vkeys import press, key_down, key_up

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/zero/'

# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    FLASH_JUMP = 'alt'
    TELEPORT = 'x' # 爆裂衝刺

    # Buffs
    BUFF_8 = '8' # 集中時間

    # Buffs Toggle

    # Attack Skills
    SKILL_A = 'a' # 月之降臨(a1)

    # special Skills
    SP_F12 = 'f12' # 輪迴

def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]
    
    if direction == 'left' or direction == 'right':
        if abs(d_x) > 20:
            if abs(d_x) >= 40:
                Teleport(direction=direction).execute()
                FlashJump().execute()
            else:
                if utils.bernoulli(0.3+0.4*(abs(d_x)-10)/100):
                    FlashJump(direction=direction).execute()
                else:
                    Teleport(direction=direction).execute()
        elif abs(d_x) > 10:
            time.sleep(utils.rand_float(0.1, 0.15))
        utils.wait_for_is_standing(500)
    
    if direction == 'up':
        if abs(d_y) > 6 :
            if abs(d_y) >= 22:
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
        Teleport(direction=direction).execute()
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
        error = utils.distance(config.player_pos, self.target)
        while config.enabled and counter > 0 and error > settings.adjust_tolerance:
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
                        Teleport(direction='down').execute()
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
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd150_buff_time > 151:
            self.cd150_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 181:
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            time.sleep(utils.rand_float(0.1, 0.3))
            press(Key.BUFF_8, 1)
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now	

class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = '二段跳'

    def __init__(self, direction="",jump='false',combo='',triple_jump="False",fast_jump="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)

    def main(self):
        self.player_jump(self.direction)
        if not self.fast_jump:
            time.sleep(utils.rand_float(0.03, 0.06)) # fast flash jump gap
        else:
            time.sleep(utils.rand_float(0.08, 0.12)) # slow flash jump gap
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1,up_time=0.05)
            if self.triple_jump:
                time.sleep(utils.rand_float(0.05, 0.08))
                press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
        key_up(self.direction,up_time=0.01)
        time.sleep(utils.rand_float(0.03, 0.06))

class Teleport(Command):
    _display_name ='爆裂衝刺'
    _distance = 27

    def __init__(self, direction = '',jump='false'):
        super().__init__(locals())
        self.direction = direction
        self.jump = jump

    def main(self):
        CustomKey(name=self._display_name,key=Key.TELEPORT,direction=self.direction,jump=self.jump,delay=0.095).execute()
