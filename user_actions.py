from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self.keyboard.unbind(on_key_down=self.on_keyboard_down)
    self.keyboard.unbind(on_key_up=self.on_keyboard_up)
    self.keyboard = None


def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_has_started:
        if touch.x < self.width/2:
            self.current_speed_x = self.SPEED_X    # LEFT CONTROL BTN
            # print("<-")
        else:
            self.current_speed_x = -self.SPEED_X   # RIGHT CONTROL BTN
            # print("->")
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    self.current_speed_x = 0   # STOP MOVEMENT
    # print("UP")


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_speed_x = self.SPEED_X  # LEFT CONTROL BTN
        # print("<-")
    elif keycode[1] == 'right':
        self.current_speed_x = -self.SPEED_X  # RIGHT CONTROL BTN
        # print("->")
    return True


def on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0  # STOP MOVEMENT
