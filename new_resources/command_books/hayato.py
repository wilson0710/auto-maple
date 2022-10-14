"""A collection of all commands that Adele can use to interact with the game. 	"""

from sqlalchemy import true
from src.common import config, settings, utils
import time
import math
from src.routine.components import Command
from src.common.vkeys import press, key_down, key_up

IMAGE_DIR = config.RESOURCES_DIR + '/command_books/hayato/'

# List of key mappings
class Key:
    # Movement
    JUMP = 'alt'
    FLASH_JUMP = 'alt'
    UP_JUMP = 'c'

    # Buffs
    BUFF_1 = 'f1' #公主的加護
    BUFF_2 = '6' #曉月勇者

    # Buffs Toggle

    # Attack Skills
    MAIN_GROUP_ATTACK_SKILL = 'a' # 三連斬
    SKILL_1 = 'd' # 曉月大太刀
    SKILL_2 = 'w' # 剎那斬
    SKILL_3 = 'e' # 指令五影劍
    SKILL_33 = 's' # 五影劍
    SKILL_4 = 'q' # 神速無雙
    SKILL_5 = '4' # 曉月流奧義-劍神
    SKILL_6 = '5' # 集結曉之陣
    SKILL_7 = 'r' # 嘯月光斬
    SKILL_8 = '3' # 百人一閃/疾風五月雨刃
    SKILL_9 = 'f' # 一閃
    SKILL_10 = 'x' # 斷空閃
    SKILL_11 = '1' # 瞬殺斬
    SKILL_12 = 'f' # 一閃角
    SKILL_V = 'v' # 鷹爪閃


#########################
#       Commands        #
#########################
def step(direction, target):
    """
    Performs one movement step in the given DIRECTION towards TARGET.
    Should not press any arrow keys, as those are handled by Auto Maple.
    """

    d_y = target[1] - config.player_pos[1]
    d_x = target[0] - config.player_pos[0]
    
    if direction == 'left' or direction == 'right':
        if abs(d_x) > 24:
            if abs(d_x) >= 30:
                Skill_10(direction='',combo='true').execute()
                MainGroupAttackSkill(direction='',attacks='1').execute()
            else:
                FlashJump(direction='',triple_jump='false',fast_jump='true').execute()
                MainGroupAttackSkill(direction='',attacks='3').execute()
                time.sleep(utils.rand_float(0.2, 0.25))
        elif abs(d_x) > 12:
            print("微調dis : ",abs(d_x))
            press(Key.JUMP, 1,down_time=0.1,up_time=0.05)
            # for i in range(10): # maximum time : 2s
            #     if config.player_states['movement_state'] == config.MOVEMENT_STATE_JUMPING:
            #         print("start jumping")
            #         break
            #     time.sleep(0.08)
            #     press(Key.JUMP, 1,up_time=0.02)
            time.sleep(0.42+(0.06*((24-abs(d_x))/13))) # add delay according to distance, max=0.1sec
            press(Key.JUMP, 1)
            MainGroupAttackSkill(direction='',attacks='1').execute()
        utils.wait_for_is_standing(300)
    
    if direction == 'up':
        if abs(d_y) > 6 :
            if abs(d_y) > 23:
                UpJump(direction='',jump='true').execute()
            else:
                UpJump(direction='',jump='false').execute()
            utils.wait_for_is_standing(300)
        else:
            press(Key.JUMP, 1)
            time.sleep(utils.rand_float(0.1, 0.15))
    if direction == 'down':
        if not config.player_states['movement_state'] == config.MOVEMENT_STATE_FALLING:
            print("down stair")
            time.sleep(utils.rand_float(0.05, 0.07))
            press(Key.JUMP, 1)
        time.sleep(utils.rand_float(0.15, 0.25))
      

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
            press(Key.BUFF_1, 2)
            time.sleep(utils.rand_float(0.6, 0.8))
            self.cd120_buff_time = now
        if self.cd180_buff_time == 0 or now - self.cd180_buff_time > 180:
            self.cd180_buff_time = now
        if self.cd200_buff_time == 0 or now - self.cd200_buff_time > 200:
            self.cd200_buff_time = now
        if self.cd240_buff_time == 0 or now - self.cd240_buff_time > 240:
            self.cd240_buff_time = now
        if self.cd900_buff_time == 0 or now - self.cd900_buff_time > 900:
            press(Key.BUFF_2, 2)
            time.sleep(utils.rand_float(0.5, 0.7))
            self.cd900_buff_time = now
        # if self.decent_buff_time == 0 or now - self.decent_buff_time > settings.buff_cooldown:
        #     for key in buffs:
        #       press(key, 3, up_time=0.3)
        #       self.decent_buff_time = now		


class FlashJump(Command):
    """Performs a flash jump in the given direction."""
    _display_name = '二段跳'

    def __init__(self, direction="left",triple_jump="False",fast_jump="false"):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.triple_jump = settings.validate_boolean(triple_jump)
        self.fast_jump = settings.validate_boolean(fast_jump)

    def main(self):
        utils.wait_for_is_standing(2000)
        key_down(self.direction)
        press(Key.JUMP, 1,up_time=0.02)
        for i in range(10): # maximum time : 2s
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_JUMPING:
                print("start jumping")
                break
            time.sleep(0.08)
            press(Key.JUMP, 1,up_time=0.02)

        if not self.fast_jump:
            time.sleep(utils.rand_float(0.1, 0.15)) # slow flash jump gap
        if self.direction == 'up':
            press(Key.FLASH_JUMP, 1)
        else:
            press(Key.FLASH_JUMP, 1,up_time=0.06)
            key_up(self.direction,up_time=0.02)
            if self.triple_jump:
                time.sleep(utils.rand_float(0.02, 0.05))
                press(Key.FLASH_JUMP, 1,down_time=0.07,up_time=0.04) # if this job can do triple jump
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
        if self.jump:
            press(Key.JUMP, 1,up_time=0.08)
            for i in range(10): # maximum time : 2s
                if config.player_states['movement_state'] == config.MOVEMENT_STATE_JUMPING:
                    print("start jumping")
                    break
                time.sleep(0.12)
                press(Key.JUMP, 1,up_time=0.08)
            time.sleep(utils.rand_float(0.04, 0.07))
        press(Key.UP_JUMP, 1,up_time=0.05)
        press(Key.SKILL_4, 1,up_time=0.05) # eliminate delay of up_jump
        key_up(self.direction)
        if self.combo:
            time.sleep(utils.rand_float(0.04, 0.07))
        else:
            time.sleep(utils.rand_float(0.4, 0.6))

# 三連斬
class MainGroupAttackSkill(Command):
    """Attacks using '三連斬' in a given direction."""
    _display_name = '三連斬'

    def __init__(self, direction, attacks=2, repetitions=1,jump='false',combo='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.jump:
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            press(Key.JUMP, 1)
        else:
            key_down(self.direction)
        for _ in range(self.repetitions):
            press(Key.MAIN_GROUP_ATTACK_SKILL, self.attacks,down_time=0.08, up_time=0.06)
        # if config.stage_fright and utils.bernoulli(0.7):
        #     time.sleep(utils.rand_float(0.1, 0.2))
        key_up(self.direction,up_time=0.02)
        if self.combo:
            if self.attacks >= 3:
                time.sleep(utils.rand_float(0.1, 0.15))
            else:
                time.sleep(utils.rand_float(0.1, 0.15))
        else:
            if self.attacks == 3:
                time.sleep(utils.rand_float(0.45, 0.48))
            else:
                time.sleep(utils.rand_float(0.45, 0.48))

# 曉月大太刀
class Skill_1(Command):
    """Uses '曉月大太刀' once."""
    _display_name = '曉月大太刀'
    skill_cool_down = 8.1
    def __init__(self, direction='left',jump='false',combo="true"):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.check_is_skill_ready():
            if self.jump:
                utils.wait_for_is_standing(2000)
                key_down(self.direction)
                press(Key.JUMP, 1)
            else:
                key_down(self.direction)
            press(Key.SKILL_1, 1)
            key_up(self.direction,up_time=0.02)
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(0.25, 0.35))
            else:
                time.sleep(utils.rand_float(1.5, 1.8))
             
# 剎那斬
class Skill_2(Command):
    """Uses '剎那斬' once."""
    _display_name = '剎那斬'
    skill_cool_down = 8.1
    skill_image = IMAGE_DIR + 'skill_2.png'

    def __init__(self):
        super().__init__(locals())

    def main(self):
        if self.check_is_skill_ready():
            press(Key.SKILL_2, 1, up_time=0.1)
            time.sleep(utils.rand_float(0.6, 0.75))
            self.set_my_last_cooldown(time.time())
        
# 指令五影劍
class Skill_3(Command):
    """Attacks using '指令五影劍' in a given direction."""
    _display_name = '指令五影劍'

    def __init__(self, direction, attacks=1, repetitions=1,jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            press(Key.JUMP, 1)
        else:
            key_down(self.direction)
        for _ in range(self.repetitions):
            press(Key.SKILL_3, self.attacks, up_time=0.05)
        key_up(self.direction,up_time=0.02)
        time.sleep(utils.rand_float(0.2, 0.25))
		
# 五影劍
class Skill_33(Command):
    """Attacks using '五影劍' in a given direction."""
    _display_name = '五影劍'

    def __init__(self, direction, attacks=1, repetitions=1,jump='false'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.attacks = int(attacks)
        self.repetitions = int(repetitions)
        self.jump = settings.validate_boolean(jump)

    def main(self):
        if self.jump:
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            press(Key.JUMP, 1)
        else:
            key_down(self.direction)
        for _ in range(self.repetitions):
            press(Key.SKILL_33, self.attacks, up_time=0.05)
        key_up(self.direction,up_time=0.02)
        time.sleep(utils.rand_float(0.2, 0.25))

# 神速無雙
class Skill_4(Command):
    """Press skill,Uses '神速無雙' once. 可消除上跳延遲"""
    _display_name = '神速無雙'

    def main(self):
        press(Key.SKILL_4, 1)

# 曉月流奧義-劍神
class Skill_5(Command):
    """Press skill,Uses '曉月流奧義-劍神' once. """
    _display_name = '曉月流奧義-劍神'
    skill_cool_down = 120
    skill_image = IMAGE_DIR + 'skill_5.png'

    def __init__(self, direction):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.check_is_skill_ready():
          utils.wait_for_is_standing(2000)
          key_down(self.direction)
          press(Key.SKILL_5, 1, up_time=0.05)
          time.sleep(utils.rand_float(0.1, 0.15))
          key_up(self.direction,up_time=0.02)
          time.sleep(utils.rand_float(0.5, 0.6))
          self.set_my_last_cooldown(time.time())

# 集結曉之陣
class Skill_6(Command):
    """Press skill,Uses '集結曉之陣' once. """
    _display_name = '集結曉之陣'
    skill_cool_down = 120
    skill_image = IMAGE_DIR + 'skill_6.png'

    def __init__(self):
        super().__init__(locals())

    def main(self):
        if self.check_is_skill_ready():
          utils.wait_for_is_standing(2000)
          press(Key.SKILL_6, 1, up_time=0.05)
          time.sleep(utils.rand_float(0.5, 0.6))
          self.set_my_last_cooldown(time.time())

# 嘯月光斬
class Skill_7(Command):
    """Press skill,Uses '嘯月光斬' once. """
    _display_name = '嘯月光斬'
    skill_cool_down = 87
    skill_image = IMAGE_DIR + 'skill_7.png'

    def __init__(self,combo="true"):
        super().__init__(locals())
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(2000)
            press(Key.SKILL_7, 1,down_time=0.2, up_time=0.1)
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(0.3, 0.5))
            else:
                time.sleep(utils.rand_float(2.8, 3))

# 百人一閃/疾風五月雨刃
class Skill_8(Command):
    """Press skill,Uses '百人一閃/疾風五月雨刃' once. """
    _display_name = '百人一閃/疾風五月雨刃'
    skill_cool_down = 120
    skill_image = IMAGE_DIR + 'skill_8.png'

    def __init__(self,combo="true"):
        super().__init__(locals())
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.check_is_skill_ready():
          utils.wait_for_is_standing(2000)
          press(Key.SKILL_8, 1)
          self.set_my_last_cooldown(time.time())
          if self.combo:
              time.sleep(utils.rand_float(0.6, 0.8))
          else:
              time.sleep(utils.rand_float(2.5, 3))

# 一閃
class Skill_9(Command):
    """Press skill,Uses '一閃' once. """
    _display_name = '一閃'
    skill_cool_down = 65
    skill_image = IMAGE_DIR + 'skill_9.png'

    def __init__(self,direction):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)

    def main(self):
        if self.check_is_skill_ready():
            utils.wait_for_is_standing(2000)
            key_down(self.direction)
            press(Key.SKILL_9, 1, up_time=0.1)
            key_up(self.direction,up_time=0.02)
            time.sleep(utils.rand_float(1.6, 1.8))
            self.set_my_last_cooldown(time.time())

# 一閃角
class Skill_12(Command):
    """Press skill,Uses '一閃角' once. """
    _display_name = '一閃角'
    skill_cool_down = 6

    def __init__(self, direction='left',jump='false',combo="false"):
        super().__init__(locals())
        self.jump = settings.validate_boolean(jump)
        self.direction = settings.validate_arrows(direction)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        if self.check_is_skill_ready():
          if self.jump:
              utils.wait_for_is_standing(2000)
              press(Key.JUMP, 1)
          key_down(self.direction)
          press(Key.SKILL_9, 1, up_time=0.05)
          time.sleep(utils.rand_float(0.1, 0.12))
          key_up(self.direction,up_time=0.02)
          self.set_my_last_cooldown(time.time())
          if self.combo:
              time.sleep(utils.rand_float(0.3, 0.5))
          else:
              time.sleep(utils.rand_float(0.8, 1))

# 斷空閃
class Skill_10(Command):
    """Press skill,Uses '斷空閃' once. """
    _display_name = '斷空閃'
    _distance = 30

    def __init__(self,direction,combo="true"):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.combo = settings.validate_boolean(combo)

    def main(self):
        key_down(self.direction)
        press(Key.SKILL_10, 1, up_time=0.1)
        time.sleep(utils.rand_float(0.05, 0.07))
        key_up(self.direction,up_time=0.02)
        if self.combo:
            time.sleep(utils.rand_float(0.03, 0.05))
        else:
            time.sleep(utils.rand_float(0.8, 0.9))

# 瞬殺斬
class Skill_11(Command):
    """Press skill,Uses '瞬殺斬' once. """
    _display_name = '瞬殺斬'

    def __init__(self,combo="true"):
        super().__init__(locals())
        self.combo = settings.validate_boolean(combo)

    def main(self):
        # utils.wait_for_is_standing(2000)
        press(Key.SKILL_11, 1)
        if self.combo:
            time.sleep(utils.rand_float(0.3, 0.4))
        else:
            time.sleep(utils.rand_float(1, 1.2))
