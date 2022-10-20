"""A collection of classes used to execute a Routine."""

import math
from pickle import FALSE
import time
from src.common import config, settings, utils
from src.common.vkeys import key_down, key_up, press


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
            self.kwargs.pop('__class__')
            self.kwargs.pop('self')

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


class Point(Component):
    """Represents a location in a user-defined routine."""

    id = '*'

    def __init__(self, x, y, frequency=1, skip='False', adjust='False'\
        , active_if_skill_ready = '', active_if_skill_cd=''):
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

    def main(self):
        """ return if these condition are not satisfied  """
        if self.active_if_skill_cd != '':
            # check if target skill name exist, if not continue next steps 
            command_book = config.bot.command_book
            target_skill_name = None
            for key in command_book:
                if key.lower() == self.active_if_skill_cd:
                    target_skill_name = command_book[key].__name__
                    break

            if target_skill_name and config.is_skill_ready_collector[target_skill_name]:
                return
        elif self.active_if_skill_ready != '':
            # check if target skill name exist, if not continue next steps 
            command_book = config.bot.command_book
            target_skill_name = None
            for key in command_book:
                if key.lower() == self.active_if_skill_ready:
                    target_skill_name = command_book[key].__name__
                    break

            if target_skill_name and not config.is_skill_ready_collector[target_skill_name]:
                return

        """Executes the set of actions associated with this Point."""
        if self.counter == 0:
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
        ,frequency_to_loop='False', active_if_skill_ready = '', active_if_skill_cd=''):
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

    def main(self):
        if self.link is None:
            print(f"\n[!] Label '{self.label}' does not exist.")
        else:
            """ return if these condition are not satisfied  """
            if self.active_if_skill_cd != '':
                # check if target skill name exist, if not continue next steps 
                command_book = config.bot.command_book
                target_skill_name = None
                for key in command_book:
                    if key.lower() == self.active_if_skill_cd:
                        target_skill_name = command_book[key].__name__
                        break

                if target_skill_name and config.is_skill_ready_collector[target_skill_name]:
                    return
            elif self.active_if_skill_ready != '':
                # check if target skill name exist, if not continue next steps 
                command_book = config.bot.command_book
                target_skill_name = None
                for key in command_book:
                    if key.lower() == self.active_if_skill_ready:
                        target_skill_name = command_book[key].__name__
                        break

                if target_skill_name and not config.is_skill_ready_collector[target_skill_name]:
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
    skill_cool_down = 0
    last_cool_down = 0

    def __init__(self, *args):
        super().__init__(*args)
        self.id = self.__class__.__name__
        
        # print(self.__dict__)
        # if 'name' in self.__dict__:
        #   print(self.__dict__['name'])
        #   self.id = self.__dict__['name']

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
            
        
    def get_my_last_cooldown(self,id):
        if id in config.skill_cd_timer:
            return config.skill_cd_timer[id]
        else: 
            return 0

    def set_my_last_cooldown(self,last_time=time.time()):
        config.skill_cd_timer[self.id] = last_time
        config.is_skill_ready_collector[self.id] = False

    @classmethod
    def set_is_skill_ready(cls,is_ready):
        config.is_skill_ready_collector[cls.__name__] = is_ready

    @classmethod
    def get_is_skill_ready(cls):
        if not cls.__name__ in config.is_skill_ready_collector:
            config.is_skill_ready_collector[cls.__name__] = False

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
        if config.is_skill_ready_collector[self.id] == True:
            return True

        last_cool_down = self.get_my_last_cooldown(self.id)
        now = time.time()
        if now - last_cool_down > self.skill_cool_down:
            config.is_skill_ready_collector[self.id] = True
            print(self.id,self._display_name," is ready to use")
            return True
        else:
            config.is_skill_ready_collector[self.id] = False
            return False


class Move(Command):
    """Moves to a given position using the shortest path based on the current Layout."""

    def __init__(self, x, y, max_steps=15):
        super().__init__(locals())
        self.target = (float(x), float(y))
        self.max_steps = settings.validate_nonnegative_int(max_steps)
        self.prev_direction = ''

    def _new_direction(self, new):
        key_down(new)
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

    def __init__(self):
        super().__init__(locals())

    def main(self):
        utils.wait_for_is_standing(500)
        key_down('down')
        if config.stage_fright and utils.bernoulli(0.5):
            time.sleep(utils.rand_float(0.2, 0.4))
        press(config.jump_button, 1, down_time=0.1)
        key_up('down')
        time.sleep(utils.rand_float(0.1, 0.2))


class Buff(Command):
    """Undefined 'buff' command for the default command book."""

    def main(self):
        print("\n[!] 'Buff' command not implemented in current command book, aborting process.")
        config.enabled = False

class SkillCombination(Command):
    """auto select skill in this combination"""

    def __init__(self, direction='',jump='false',target_skills=''):
        super().__init__(locals())
        self.direction = settings.validate_horizontal_arrows(direction)
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

