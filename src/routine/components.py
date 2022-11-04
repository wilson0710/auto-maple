"""A collection of classes used to execute a Routine."""

import math
from pickle import FALSE
import time
from src.common import config, settings, utils
from src.common.vkeys import click, key_down, key_up, press
from src.routine.maps import WorldMap
from src.modules.listener import Listener

#################################
#       Routine Components      #
#################################
class Component:
    id = 'Routine Component'
    PRIMITIVES = {int, str, bool, float}

    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('Component superclass __init__ only accepts 1 (optional) argument: LOCALS')
        if len(kwargs) != 0:
            raise TypeError('Component superclass __init__ does not accept any keyword arguments')
        if len(args) == 0:
            self.kwargs = {}
        elif type(args[0]) != dict:
            raise TypeError("Component superclass __init__ only accepts arguments of type 'dict'.")
        else:
            self.kwargs = args[0].copy()
            if '__class__' in self.kwargs:
                self.kwargs.pop('__class__')
            if 'self' in self.kwargs:
                self.kwargs.pop('self')
            # if not 'active_if_skill_ready' in self.kwargs:
            #     self.kwargs['active_if_skill_ready'] = ""

    @utils.run_if_enabled
    def execute(self):
        self.main()

    def main(self):
        pass

    def update(self, *args, **kwargs):
        """Updates this Component's constructor arguments with new arguments."""

        self.__class__(*args, **kwargs)     # Validate arguments before actually updating values
        self.__init__(*args, **kwargs)

    def info(self):
        """Returns a dictionary of useful information about this Component."""

        return {
            'name': self.__class__.__name__,
            'vars': self.kwargs.copy()
        }

    def encode(self):
        """Encodes an object using its ID and its __init__ arguments."""

        arr = [self.id]
        for key, value in self.kwargs.items():
            if key != 'id' and type(self.kwargs[key]) in Component.PRIMITIVES:
                arr.append(f'{key}={value}')
        return ', '.join(arr)

    def check_should_active(self):
        '''
            check should active command if pass all conditions
        '''
        if self.active_if_skill_ready:
            if not utils.get_if_skill_ready(self.active_if_skill_ready.lower()):
                return False
        if self.active_if_skill_cd:
            if utils.get_if_skill_ready(self.active_if_skill_cd.lower()):
                return False
        if self.active_if_in_skill_buff:
            if not utils.get_is_in_skill_buff(self.active_if_in_skill_buff.lower()):
                return False
        if self.active_if_not_in_skill_buff:
            if utils.get_is_in_skill_buff(self.active_if_not_in_skill_buff.lower()):
                return False
        return True


class Point(Component):
    """Represents a location in a user-defined routine."""

    id = '*'

    def __init__(self, x, y, frequency=1, skip='False', adjust='False'\
        , active_if_skill_ready = '', active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=""):
        super().__init__(locals())
        self.x = float(x)
        self.y = float(y)
        self.location = (self.x, self.y)
        self.frequency = settings.validate_nonnegative_int(frequency)
        self.counter = int(settings.validate_boolean(skip))
        self.adjust = settings.validate_boolean(adjust)
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        if not hasattr(self, 'commands'):       # Updating Point should not clear commands
            self.commands = []
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def main(self):
        if not self.check_should_active():
            return

        """Executes the set of actions associated with this Point."""
        if self.counter == 0:
            if self.location != (-1,-1):
                move = config.bot.command_book['move']
                move(*self.location).execute()
                if self.adjust:
                    adjust = config.bot.command_book.get('adjust')      # TODO: adjust using step('up')?
                    adjust(*self.location).execute()
            for command in self.commands:
                command.execute()
        time.sleep(utils.rand_float(0.02, 0.08))
        self._increment_counter()

    @utils.run_if_enabled
    def _increment_counter(self):
        """Increments this Point's counter, wrapping back to 0 at the upper bound."""

        self.counter = (self.counter + 1) % self.frequency

    def info(self):
        curr = super().info()
        curr['vars'].pop('location', None)
        curr['vars']['commands'] = ', '.join([c.id for c in self.commands])
        return curr

    def __str__(self):
        return f'  * {self.location}'


class Label(Component):
    id = '@'

    def __init__(self, label):
        super().__init__(locals())
        self.label = str(label)
        if self.label in config.routine.labels:
            raise ValueError
        self.links = set()
        self.index = None

    def set_index(self, i):
        self.index = i

    def encode(self):
        return '\n' + super().encode()

    def info(self):
        curr = super().info()
        curr['vars']['index'] = self.index
        return curr

    def __delete__(self, instance):
        del self.links
        config.routine.labels.pop(self.label)

    def __str__(self):
        return f'{self.label}:'


class Jump(Component):
    """Jumps to the given Label."""

    id = '>'

    def __init__(self, label, frequency=1, skip='False'\
        ,frequency_to_loop='False', active_if_skill_ready = '', active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=''):
        super().__init__(locals())
        self.label = str(label)
        self.frequency = settings.validate_nonnegative_int(frequency)
        self.counter = int(settings.validate_boolean(skip))
        self.link = None
        self.frequency_to_loop = settings.validate_boolean(frequency_to_loop)
        if self.frequency_to_loop:
            self.counter = 1
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def main(self):
        if self.link is None:
            print(f"\n[!] Label '{self.label}' does not exist.")
        else:
            if not self.check_should_active():
                return

            if self.counter == 0 and not self.frequency_to_loop:
                config.routine.index = self.link.index
            elif self.counter != 0 and self.frequency_to_loop:
                config.routine.index = self.link.index
            self._increment_counter()

    @utils.run_if_enabled
    def _increment_counter(self):
        self.counter = (self.counter + 1) % self.frequency

    def bind(self):
        """
        Binds this Goto to its corresponding Label. If the Label's index changes, this Goto
        instance will automatically be able to access the updated value.
        :return:    Whether the binding was successful
        """

        if self.label in config.routine.labels:
            self.link = config.routine.labels[self.label]
            self.link.links.add(self)
            return True
        return False

    def __delete__(self, instance):
        if self.link is not None:
            self.link.links.remove(self)

    def __str__(self):
        return f'  > {self.label}'


class Setting(Component):
    """Changes the value of the given setting variable."""

    id = '$'

    def __init__(self, target, value):
        super().__init__(locals())
        self.key = str(target)
        if self.key not in settings.SETTING_VALIDATORS:
            raise ValueError(f"Setting '{target}' does not exist")
        self.value = settings.SETTING_VALIDATORS[self.key](value)

    def main(self):
        setattr(settings, self.key, self.value)

    def __str__(self):
        return f'  $ {self.key} = {self.value}'


SYMBOLS = {
    '*': Point,
    '@': Label,
    '>': Jump,
    '$': Setting
}


#############################
#       Shared Commands     #
#############################
class Command(Component):
    id = 'Command Superclass'
    _display_name = ""
    _custom_id = ""
    skill_cool_down = 0
    last_cool_down = 0

    def __init__(self, *args):
        super().__init__(*args)
        self.id = self.__class__.__name__
        self._custom_id = self.id
        self.set_my_last_cooldown(0)

    def __str__(self):
        variables = self.__dict__
        result = '    ' + self.id
        if len(variables) - 1 > 0:
            result += ':'
        for key, value in variables.items():
            if key != 'id':
                result += f'\n        {key}={value}'
        return result

    def player_jump(self,direction=""):
        utils.wait_for_is_standing(1500)
        key_down(direction)
        press(config.jump_button, 1,up_time=0.05)
        for i in range(100): # maximum time : 2s
            if config.player_states['movement_state'] == config.MOVEMENT_STATE_JUMPING:
                time.sleep(utils.rand_float(0.02, 0.04))
                break
            if i % 10 == 9:
                press(config.jump_button, 1,up_time=0.05)
            else:
                time.sleep(0.02)
            
    def check_should_active(self):
        '''
            check should active command if pass all conditions
        '''
        if self.active_if_skill_ready:
            if not utils.get_if_skill_ready(self.active_if_skill_ready.lower()):
                return False
        if self.active_if_skill_cd:
            if utils.get_if_skill_ready(self.active_if_skill_cd.lower()):
                return False
        if self.active_if_in_skill_buff:
            if not utils.get_is_in_skill_buff(self.active_if_in_skill_buff.lower()):
                return False
        if self.active_if_not_in_skill_buff:
            if utils.get_is_in_skill_buff(self.active_if_not_in_skill_buff.lower()):
                return False
        return True

    def get_my_last_cooldown(self,id):
        if id in config.skill_cd_timer:
            return config.skill_cd_timer[id]
        else: 
            return 0

    def set_my_last_cooldown(self,last_time=time.time()):
        config.skill_cd_timer[self._custom_id] = last_time
        if self.skill_cool_down != 0:
            config.is_skill_ready_collector[self._custom_id] = False

    @classmethod
    def set_is_skill_ready(cls,is_ready):
        config.is_skill_ready_collector[cls.__name__] = is_ready

    @classmethod
    def get_is_skill_ready(cls):
        if not cls.__name__ in config.is_skill_ready_collector:
            config.is_skill_ready_collector[cls.__name__] = False

        if not cls.__name__ in config.skill_cd_timer:
            config.skill_cd_timer[cls.__name__] = 0

        if config.is_skill_ready_collector[cls.__name__] == True:
            return True

        last_cool_down = cls.get_my_last_cooldown(cls,cls.__name__)
        now = time.time()
        if now - last_cool_down > cls.skill_cool_down:
            config.is_skill_ready_collector[cls.__name__] = True
            print(cls.__name__,cls._display_name," is ready to use CD:",cls.skill_cool_down)
            return True
        else:
            config.is_skill_ready_collector[cls.__name__] = False
            return False

    def check_is_skill_ready(self):
        if config.is_skill_ready_collector[self._custom_id] == True:
            return True

        last_cool_down = self.get_my_last_cooldown(self._custom_id)
        now = time.time()
        if now - last_cool_down > self.skill_cool_down:
            config.is_skill_ready_collector[self._custom_id] = True
            # print(self._custom_id,self._display_name," is ready to use")
            return True
        else:
            config.is_skill_ready_collector[self._custom_id] = False
            return False


class Move(Command):
    """Moves to a given position using the shortest path based on the current Layout."""

    def __init__(self, x, y, max_steps=15):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)
        self.prev_direction = ''

    def _new_direction(self, new):
        key_down(new,down_time=0.05)
        if self.prev_direction and self.prev_direction != new:
            key_up(self.prev_direction)
        self.prev_direction = new

    def _new_move_method(self,target):
        pass

    def main(self):
        counter = self.max_steps
        path = config.layout.shortest_path(config.player_pos, self.target)
        for i, point in enumerate(path):
            toggle = True
            self.prev_direction = ''
            local_error = utils.distance(config.player_pos, point)
            global_error = utils.distance(config.player_pos, self.target)
            d_x = point[0] - config.player_pos[0]
            d_y = point[1] - config.player_pos[1]
            # prevent change map error
            if config.player_pos[0] == 0 and config.player_pos[1] == 0:
                step("left", (-30,30))
            while config.enabled and counter > 0 and \
                    local_error > settings.move_tolerance and \
                    global_error > settings.move_tolerance or \
                    abs(d_y) > settings.move_tolerance / 2:
                if toggle:
                    d_x = point[0] - config.player_pos[0]
                    if abs(d_x) > settings.move_tolerance / math.sqrt(2):
                        if d_x < 0:
                            key = 'left'
                        else:
                            key = 'right'
                        self._new_direction(key)
                        step(key, point)
                        if settings.record_layout:
                            config.layout.add(*config.player_pos)
                        counter -= 1
                        time.sleep(0.02)
                else:
                    d_y = point[1] - config.player_pos[1]
                    if abs(d_y) > settings.move_tolerance / 2:
                        if d_y < 0:
                            key = 'up' # if direction=up dont press up to avoid transporter
                            if abs(d_x) < settings.move_tolerance / math.sqrt(2): # key up horizontal arrow if inside move_tolerance 
                                self._new_direction('')
                        else:
                            key = 'down'
                            if config.player_states['in_bottom_platform'] == False:
                                self._new_direction(key)
                        step(key, point)
                        if settings.record_layout:
                            config.layout.add(*config.player_pos)
                        counter -= 1
                        time.sleep(0.02)
                local_error = utils.distance(config.player_pos, point)
                global_error = utils.distance(config.player_pos, self.target)
                toggle = not toggle
            if self.prev_direction:
                key_up(self.prev_direction)


class Adjust(Command):
    """Fine-tunes player position using small movements."""

    def __init__(self, x, y, max_steps=5):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)


def step(direction, target):
    """
    The default 'step' function. If not overridden, immediately stops the bot.
    :param direction:   The direction in which to move.
    :param target:      The target location to step towards.
    :return:            None
    """

    print("\n[!] Function 'step' not implemented in current command book, aborting process.")
    config.enabled = False


class Wait(Command):
    """Waits for a set amount of time."""

    def __init__(self, duration):
        super().__init__(locals())
        self.duration = float(duration)

    def main(self):
        time.sleep(utils.rand_float(self.duration*0.8, self.duration*1.2))
        


class Walk(Command):
    """Walks in the given direction for a set amount of time."""

    def __init__(self, direction, duration):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.duration = float(duration)

    def main(self):
        key_down(self.direction)
        time.sleep(utils.rand_float(self.duration*0.8, self.duration*1.2))
        key_up(self.direction)


class Fall(Command):
    """
    Performs a down-jump and then free-falls until the player exceeds a given distance
    from their starting position.
    """

    def __init__(self, direction='', duration='0.1'):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
        self.duration = float(duration)

    def main(self):
        utils.wait_for_is_standing(500)
        key_down('down')
        if config.stage_fright and utils.bernoulli(0.5):
            time.sleep(utils.rand_float(0.2, 0.4))
        press(config.jump_button, 2, down_time=self.duration)
        key_up('down')
        if self.direction != '':
            key_down(self.direction)
            press(config.jump_button, 2, down_time=0.1)
            key_up(self.direction)
        time.sleep(utils.rand_float(0.08, 0.12))


class Buff(Command):
    """Undefined 'buff' command for the default command book."""

    def main(self):
        print("\n[!] 'Buff' command not implemented in current command book, aborting process.")
        config.enabled = False

class CustomKey(Command):
    """users define their custom function of target key """
    _display_name = '自定義按鍵'
    # skill_cool_down = 0

    def __init__(self,name='',key='', direction='',jump='false',delay='0.5',rep='1',rep_interval='0.3',rep_interval_increase='0',duration='0',cool_down='0',ground_skill='true',buff_time='',active_if_skill_ready='',active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=''):
        super().__init__(locals())
        self._display_name = name
        self.key = key
        self._custom_id = 'custom_key_' + key
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.delay = float(delay)
        self.rep = settings.validate_nonnegative_int(rep)
        self.rep_interval = float(rep_interval)
        self.rep_interval_increase = float(rep_interval_increase)
        self.duration = float(duration)
        self.skill_cool_down = float(cool_down)
        self.ground_skill = settings.validate_boolean(ground_skill)
        config.is_skill_ready_collector[self._custom_id] = True
        self.buff_time = buff_time
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def main(self):
        if not self.check_should_active():
            return
        if self.skill_cool_down == 0 or self.check_is_skill_ready():
            if self.ground_skill:
                utils.wait_for_is_standing(1000)

            if self.jump:
                self.player_jump(self.direction)
                # time.sleep(utils.rand_float(0.02, 0.05))
            else:
                key_down(self.direction)
            time.sleep(utils.rand_float(0.03, 0.07))
            for i in range(self.rep):
                key_down(self.key,down_time=0.07)
                if self.duration != 0:
                    time.sleep(utils.rand_float(self.duration*0.9, self.duration*1.1))
                key_up(self.key,up_time=0.05)
                if i != (self.rep-1):
                    ret_interval = self.rep_interval+self.rep_interval_increase*i
                    time.sleep(utils.rand_float(ret_interval*0.92, ret_interval*1.08))
            key_up(self.direction,up_time=0.01)
            # if self.skill_cool_down != 0:
            self.set_my_last_cooldown(time.time())
            time.sleep(utils.rand_float(self.delay*0.8, self.delay*1.2))

class BaseSkill(Command):
    """pre define base skill class """
    _display_name = ""
    key=''
    delay=0.5
    rep_interval=0.3
    skill_cool_down=0
    ground_skill=True
    buff_time=0
    combo_delay = 0.1
    rep_interval_increase = 0

    def __init__(self, direction='',jump='false',rep='1',duration='0',combo='false',active_if_skill_ready='',active_if_skill_cd='',active_if_in_skill_buff='',active_if_not_in_skill_buff=''):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = settings.validate_boolean(jump)
        self.rep = settings.validate_nonnegative_int(rep)
        self.duration = float(duration)
        config.is_skill_ready_collector[self._custom_id] = True
        self.combo = settings.validate_boolean(combo)
        self.active_if_skill_ready = active_if_skill_ready
        self.active_if_skill_cd = active_if_skill_cd
        self.active_if_in_skill_buff = active_if_in_skill_buff
        self.active_if_not_in_skill_buff = active_if_not_in_skill_buff

    def main(self):
        if not self.check_should_active():
            return
        if self.skill_cool_down == 0 or self.check_is_skill_ready():
            if self.ground_skill:
                utils.wait_for_is_standing(1000)

            if self.jump:
                self.player_jump(self.direction)
                time.sleep(utils.rand_float(0.02, 0.05))
            else:
                key_down(self.direction)
            # time.sleep(utils.rand_float(0.03, 0.07))
            for i in range(self.rep):
                key_down(self.key,down_time=0.07)
                if self.duration != 0:
                    time.sleep(utils.rand_float(self.duration*0.9, self.duration*1.1))
                key_up(self.key,up_time=0.05)
                if i != (self.rep-1):
                    ret_interval = self.rep_interval+self.rep_interval_increase*i
                    time.sleep(utils.rand_float(ret_interval*0.92, ret_interval*1.08))
            key_up(self.direction,up_time=0.01)
            # if self.skill_cool_down != 0:
            self.set_my_last_cooldown(time.time())
            if self.combo:
                time.sleep(utils.rand_float(self.combo_delay*0.9, self.combo_delay*1.1))
            else:
                time.sleep(utils.rand_float(self.delay*0.9, self.delay*1.1))

class SkillCombination(Command):
    """auto select skill in this combination"""
    # _display_name = '自定義按鍵'

    def __init__(self, direction='',jump='false',target_skills=''):
        super().__init__(locals())
        self.direction = settings.validate_arrows(direction)
        self.jump = jump
        self.target_skills = target_skills
        
    def main(self):
        skills_array = self.target_skills.split("|")
        for skill in skills_array:
            skill = skill.lower()
            if "+" in skill:
                combo_skills = skill.split('+')
                s = config.bot.command_book[combo_skills[0]]
                if not s.get_is_skill_ready():
                    continue
                s(direction=self.direction,jump=self.jump,combo="true").execute()
                s = config.bot.command_book[combo_skills[1]]
                s(direction=self.direction,jump="false").execute()
                break
            else:
                s = config.bot.command_book[skill]
                if not s.get_is_skill_ready():
                    continue
                else:
                    s(direction=self.direction,jump=self.jump).execute()
                    break

class GoToMap(Command):
    """ go to target map """
    _display_name = '前往地圖'
    # skill_cool_down = 0

    def __init__(self,target_map=''):
        super().__init__(locals())
        self.target_map = target_map

    def main(self):
        wm = WorldMap()
        if wm.check_if_in_correct_map(self.target_map):
            return
        press('n') # big map key
        time.sleep(utils.rand_float(0.3*0.8, 0.3*1.2))
        wm = WorldMap()
        if self.target_map in wm.maps_info:
            config.map_changing = True
            target_map_info = wm.maps_info[self.target_map]
            utils.game_window_click(wm.WORLD_MENU)
            utils.game_window_click(target_map_info['world_selection_point'])
            utils.game_window_click(wm.AREA_MENU)
            utils.game_window_click(target_map_info['area_selection_point'])
            time.sleep(utils.rand_float(0.3*0.8, 0.3*1.2))
            utils.game_window_click(target_map_info['point'],click_time=2)
            press('enter')
            time.sleep(1)
            for _ in range(10):
                if wm.check_if_in_correct_map(self.target_map):
                    break
                time.sleep(0.3)
            Listener.recalibrate_minimap()
            time.sleep(0.2)
            config.map_changing = False
        else:
            pass # use search to reach map
