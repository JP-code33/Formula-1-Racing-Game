import pygame
import time
import math 
from utils import scale_image, blit_rotate_center

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"),2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"),0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"),0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER) 
FINISH = scale_image(pygame.image.load("imgs/Finish_line.png"), 0.22)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (138, 250)
REDBULL_CAR = scale_image(pygame.image.load("imgs/rb22.png"),0.03)
W17_CAR = scale_image(pygame.image.load("imgs/w17.png"),0.0265)
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formula 1 Racing Game")


FPS = 60
PATH = [(190, 127), (117, 61), (46, 134), (69, 474), (351, 738), (402, 693), (413, 520), (510, 467), (604, 542), (666, 741), (744, 691), (735, 439), (682, 372), (457, 380), (404, 320), (466, 254), (687, 266), (738, 220), (744, 124), (670, 76), (359, 75), (282, 146), (266, 346), (234, 406), (161, 343), (176, 263)]

class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
            self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
            self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0



class PlayerCar(AbstractCar):
    IMG = REDBULL_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.acceleration / 2, 0)

        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    IMG = W17_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        #self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff/y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

def draw(win, images, player_car, computer_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def move_player(player_car):

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()
    if not moved:
        player_car.reduce_speed()

def handle_collision(player_car, Computer_car):
    if player_car.collide(TRACK_BORDER_MASK) != None:
            player_car.bounce()
    
    Computer_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if Computer_finish_poi_collide != None:
            player_car.reset()
            Computer_car.reset()
    
    
    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            print(player_finish_poi_collide)
            player_car.bounce()
        else:
            player_car.reset()
            Computer_car.reset()
            print("finish")

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))]
player_car = PlayerCar(3.5,3.5)
Computer_car = ComputerCar(2.5,3.5,PATH)

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, Computer_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        #if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            Computer_car.path.append(pos)
        
    move_player(player_car)
    Computer_car.move()
    handle_collision(player_car, Computer_car)

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    Computer_finish_poi_collide = Computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if Computer_finish_poi_collide != None:
        player_car.reset()
        Computer_car.reset()


    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            print(player_finish_poi_collide)
            player_car.bounce()
        else:
            player_car.reset()
            Computer_car.reset()
            print("finish")

print(Computer_car.path)

pygame.quit()


                                           