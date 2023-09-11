import random

from kivy.config import Config
# ------------ Window size configuration ----------
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
# --------------------------------------------------

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    score_txt = StringProperty("SCORE: 0")

    PERSPECTIVE = 0.75

    NB_V_LINES = 8
    V_LINES_SPACING = 0.4
    vertical_lines = []

    NB_H_LINES = 15
    H_LINES_SPACING = 0.15
    horizontal_lines = []

    NB_Tiles = 16
    tiles = []
    tiles_coordinates = []

    SPEED = .8           # vertical movt speed
    current_offset_y = 0

    SPEED_X = 3.0   # Button Movt control Speed
    current_speed_x = 0
    current_offset_x = 0
    current_y_loop = 0

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordintes = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_has_started = False

    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W: " + str(self.width) + " H: " + str(self.height))

        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()
        self.sound_galaxy.play()
        # self.pre_fill_tiles_coordinates()
        # self.generate_tiles_coordinates()

        if self.is_desktop():  # calling function checking if device is PC or phones
            self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self.keyboard.bind(on_key_down=self.on_keyboard_down)
            self.keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60)

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6

    def reset_game(self):
        self.current_offset_y = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.current_y_loop = 0

        self.score_txt = "SCORE: " + str(self.current_y_loop)
        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    def is_desktop(self):  # function checking if device is PC or phones
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def on_size(self, *args):
        # print("INIT W: " + str(self.width) + " H: " + str(self.height))
        # self.perspective_point_x = self.width/2
        # self.perspective_point_y = self.height * 0.75

        # self.update_vertical_line()
        # self.update_horizontal_line()
        pass

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.height * self.SHIP_HEIGHT
        self.ship_coordintes[0] = (center_x - ship_half_width, base_y)
        self.ship_coordintes[1] = (center_x, base_y + ship_height)
        self.ship_coordintes[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordintes[0])
        x2, y2 = self.transform(*self.ship_coordintes[1])
        x3, y3 = self.transform(*self.ship_coordintes[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordintes[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.width * self.V_LINES_SPACING
        offset = index - 0.5
        line_x = central_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index*spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1
        # print('foo1')

        for i in range(len(self.tiles_coordinates), self.NB_Tiles):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.NB_V_LINES / 2) + 1
            end_index = start_index + self.NB_V_LINES - 2
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1
        # print('foo2')

# -------------------------- BUILDING TILES ----------------------
    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_Tiles):
                self.tiles.append(Quad())

    def update_tiles(self):
        for i in range(0, self.NB_Tiles):
            tile = self.tiles[i]
            tiles_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tiles_coordinates[0], tiles_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tiles_coordinates[0]+1, tiles_coordinates[1]+1)

            # 2     3
            #
            # 1     4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]
# --------------------------------------------------------------------------------------

# -------------------- VERTICAL LINE CODE ---------------------------
    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_V_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_line(self):
        start_index = -int(self.NB_V_LINES/2)+1
        for i in range(start_index, start_index+self.NB_V_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

# -------------------- HORIZOTAL LINE CODE ---------------------------
    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_H_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_line(self):
        start_index = -int(self.NB_V_LINES / 2) + 1
        end_index = start_index+self.NB_V_LINES - 1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.NB_H_LINES):
            line_y = self.get_line_y_from_index(i)  # horizontal shifting movt
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]
# -------------------------------------------------------------------------------------

    def update(self, dt):
        # print("dt: " + str(dt) + "1/50: " + str(1/60))
        time_factor = dt * 60  # for correcting timing difference from various device
        self.update_vertical_line()
        self.update_horizontal_line()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED * self.height/100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE: " + str(self.current_y_loop)
                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.width/100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "G  A  M  E   O  V  E  R"
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            print("GAME OVER")
            self.sound_gameover_impact.play()
            self.sound_music1.stop()
            Clock.schedule_once(self.play_sound_game_over, 3)

    def play_sound_game_over(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def on_menu_button_pressed(self):
        print("button")
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0



class GalaxyApp(App):
    pass


GalaxyApp().run()
