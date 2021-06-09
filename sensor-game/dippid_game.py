import random
import sys, math
from PyQt5 import QtGui, QtCore, QtWidgets, uic
from enum import Enum
from datetime import datetime
from DIPPID import SensorUDP, SensorCapabilities

BRICKS_PER_ROW = 10
NUM_ROWS = 5

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_SPEED = 6

BALL_DIAMETER = 20
BALL_SPEED = 2

app = QtWidgets.QApplication(sys.argv)


class GameState(Enum):
    INTRO = 1
    STARTED = 2
    WON = 3
    LOST = 4


class CollisionDirection(Enum):
    LEFT_RIGHT = 1
    TOP_BOTTOM = 2


class Brick(QtCore.QRect):

    def __init__(self, hits_to_break, x, y, width, height):
        super().__init__(x, y, width, height)
        self.hits_to_break = hits_to_break


class Paddle(QtCore.QRect):

    def __init__(self, x, y, width, height, window):
        super().__init__(x, y, width, height)
        self.paddle_width = width
        self.paddle_height = height
        self.window = window

    def move(self, delta):
        self.moveLeft(self.x() + delta)

        if self.x() < 0:
            self.moveLeft(0)
        elif self.x() > self.window.frameGeometry().width() - self.paddle_width:
            self.moveLeft(self.window.frameGeometry().width() - self.paddle_width)


class Ball:

    def __init__(self, x, y, diameter, window):
        self.x = x
        self.y = y
        self.diameter = diameter
        self.radius = diameter / 2
        self.window = window
        self.speed_x = BALL_SPEED
        self.speed_y = -BALL_SPEED

    def y_center(self):
        return self.y + self.radius

    def x_center(self):
        return self.x + self.radius

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        self.check_for_collisions()
        self.check_for_game_over()

    def check_for_collisions(self):
        self.check_for_window_collision()
        self.check_for_paddle_collision()
        self.check_for_brick_collision()

    def check_for_brick_collision(self):
        for brick in self.window.bricks[:]:
            collision = self.intersects_rectangle(brick)
            if collision == CollisionDirection.TOP_BOTTOM:
                self.on_brick_hit(brick)
                self.speed_y *= -1
            elif collision == CollisionDirection.LEFT_RIGHT:
                self.on_brick_hit(brick)
                self.speed_x *= -1

    def check_for_paddle_collision(self):
        collision = self.intersects_rectangle(self.window.paddle)
        if collision == CollisionDirection.TOP_BOTTOM:
            self.speed_y *= -1
        elif collision == CollisionDirection.LEFT_RIGHT:
            self.speed_x *= -1

    def check_for_window_collision(self):
        if self.x + self.radius * 2 > self.window.frameGeometry().width() or self.x <= 0:
            self.speed_x *= -1

        elif self.y <= 0:
            self.speed_y *= -1

    def intersects_rectangle(self, rect):
        test_x = self.x_center()
        test_y = self.y_center()

        if self.x_center() < rect.left():
            test_x = rect.left()
        elif self.x_center() > rect.right():
            test_x = rect.right()

        if self.y_center() > rect.bottom():
            test_y = rect.bottom()
        elif self.y_center() < rect.top():
            test_y = -rect.top()

        dist_x = self.x_center() - test_x
        dist_y = self.y_center() - test_y
        distance = math.sqrt(dist_x * dist_x + dist_y * dist_y)

        if distance <= self.radius:
            if dist_x == 0:
                return CollisionDirection.TOP_BOTTOM
            elif dist_y == 0:
                return CollisionDirection.LEFT_RIGHT

        return False

    def clamp(self, num, min_value, max_value):
        return max(min(num, max_value), min_value)

    def check_for_game_over(self):
        if self.y > self.window.frameGeometry().height():
            self.window.game_state = GameState.LOST

    def on_brick_hit(self, brick):
        brick.hits_to_break -= 1

        if brick.hits_to_break <= 0:
            self.window.bricks.remove(brick)


class PongPing(QtWidgets.QWidget):

    sensor = ()
    paddle = ()
    ball = ()
    timer = ()
    last_frame_timestamp = None
    bricks = []

    def __init__(self):
        super().__init__()
        self.win = uic.loadUi("game.ui")
        self.game_state = GameState.INTRO

        self.init_sensor()
        self.init_bricks()
        self.init_paddle()
        self.init_ball()
        self.init_game_loop_timer()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        self.draw_bricks(painter)
        self.draw_paddle(painter)
        self.draw_ball(painter)

    def draw_bricks(self, painter):
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine))

        for brick in self.bricks:
            self.set_brush_to_brick_color(brick, painter)
            painter.drawRect(brick)

    def draw_paddle(self, painter):
        painter.setBrush(QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern))
        painter.drawRect(self.paddle)

    def draw_ball(self, painter):
        painter.setBrush(QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
        painter.drawEllipse(self.ball.x, self.ball.y, self.ball.radius, self.ball.radius)

    def init_bricks(self):
        width = self.frameGeometry().width() / BRICKS_PER_ROW
        height = (self.frameGeometry().height() / 2) / NUM_ROWS
        for x in range(0, BRICKS_PER_ROW):
            for y in range(0, NUM_ROWS):
                hits_to_break = random.randrange(1, 4)
                self.bricks.append(Brick(hits_to_break, x * width, y * height, width, height))

    def init_paddle(self):
        xPos = self.frameGeometry().width() / 2 - PADDLE_WIDTH / 2
        yPos = self.frameGeometry().height() - 20  # seems like a good default height for the paddle

        self.paddle = Paddle(xPos, yPos, PADDLE_WIDTH, PADDLE_HEIGHT, self)

    def init_sensor(self):
        self.sensor = SensorUDP(5700)
        self.sensor.register_callback(SensorCapabilities.BUTTON_1, self.handle_button_1_press)

    def init_ball(self):
        xPos = self.paddle.x() + self.paddle.paddle_width / 2
        yPos = self.paddle.y() - BALL_DIAMETER - 5
        self.ball = Ball(xPos, yPos, BALL_DIAMETER, self)

    def init_game_loop_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.game_loop)

        self.timer.start(int(1000 / 60))

    def handle_button_1_press(self, data):
        if data == 0:
            return

        if self.game_state == GameState.INTRO:
            self.game_state = GameState.STARTED

        if self.game_state == GameState.LOST:
            self.restart_game()

    def restart_game(self):
        self.bricks = []
        self.init_bricks()

        self.init_ball()

        self.update()
        self.game_state = GameState.INTRO

    def game_loop(self):
        if self.game_state == GameState.STARTED:
            self.move_paddle()
            self.move_ball()

            self.update()

    def move_paddle(self):
        if self.sensor.has_capability(SensorCapabilities.ACCELEROMETER):
            sensorVal = self.sensor.get_value(SensorCapabilities.ACCELEROMETER)
        else:
            return

        y_value = sensorVal['y']

        self.paddle.move(y_value * PADDLE_SPEED)

    def set_brush_to_brick_color(self, brick, painter):
        if brick.hits_to_break > 3:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
        elif brick.hits_to_break == 3:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.blue, QtCore.Qt.SolidPattern))
        elif brick.hits_to_break == 2:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.green, QtCore.Qt.SolidPattern))
        elif brick.hits_to_break == 1:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.yellow, QtCore.Qt.SolidPattern))

    def move_ball(self):
        self.ball.move()


if __name__ == "__main__":
    game = PongPing()
    app.exec()
