import sys
import pygame
import time
import math 
from utils import scale_image, blit_rotate_center, blit_text_center
pygame.font.init()
pygame.mixer.init()

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"),2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"),0.9)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"),0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER) 
FINISH = scale_image(pygame.image.load("imgs/Finish_line.png"), 0.22)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (138, 250)
REDBULL= scale_image(pygame.image.load("imgs/rb22.png"),0.03)
MERCEDES = scale_image(pygame.image.load("imgs/w17.png"),0.0265)
FERRARI = scale_image(pygame.image.load("imgs/Ferrari.png"), 0.0475)
MCLAREN = scale_image(pygame.image.load("imgs/Mclaren.png"), 0.0140)
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Formula 1 Style Racing Game")
MAIN_FONT = pygame.font.SysFont("comicsans", 20)
BUTTON_SOUND = pygame.mixer.Sound("audio/buttonClick.mp3")
START_SOUND = pygame.mixer.Sound("audio/startLightedited.mp3")
LIGHT_RADIUS = 22
LIGHT_SPACING = 18
CARS = [
    ("Red Bull", REDBULL),
    ("Mercedes", MERCEDES),
    ("Ferrari", FERRARI),
    ("McLaren", MCLAREN)
]


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

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0 
        return round(time.time() - self.level_start_time)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

        self.font = pygame.font.SysFont("comicsans", 32)
        self.normal_color = (40,40,40)
        self.hover_color = (220,30,30)
        self.text_color = (255,255,255)

    def draw(self, win):
        mouse = pygame.mouse.get_pos()
        color = self.normal_color
        if self.rect.collidepoint(mouse):
            color = self.hover_color
        pygame.draw.rect(win, color, self.rect, border_radius=12)
        text = self.font.render(self.text, True, self.text_color)
        win.blit(text, (self.rect.centerx - text.get_width() // 2, self.rect.centery - text.get_height() // 2),)

    def clicked(self, event):
        return(event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos))
                
class AbstractCar:
    def __init__(self, max_vel, rotation_vel, img):
        self.img = img
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
    
    START_POS = (180, 200)

    def reduce_speed(self):
        if self.vel > 0:
            self.vel = max(self.vel - self.acceleration / 2, 0)
        elif self.vel < 0:
            self.vel = min(self.vel + self.acceleration / 2, 0)

        self.move()

    def __init__(self, img, max_vel, rotation_vel):
        super().__init__(max_vel, rotation_vel, img)

    def bounce(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    
    START_POS = (150, 200)

    #def __init__(self, max_vel, rotation_vel, path=[]):
        #super().__init__(max_vel, rotation_vel)
        #self.path = path
        #self.current_point = 0
        #self.vel = max_vel

    def __init__(self, img, max_vel, rotation_vel, path):
        super().__init__(max_vel, rotation_vel, img)
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

    #def reset(self):
        #super().reset()
        #self.current_point = 0
        #self.vel = self.max_vel

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2
        self.current_point = 0



def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() -70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() -40))

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() -10))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

def start_lights():
    for lights_on in range(1,6):
        START_SOUND.play()
        start = time.time()
        while time.time() - start < 1:
            WIN.fill((20,20,20))
            title = pygame.font.SysFont("comicsans", 45).render("Get Ready!", True, (255, 255, 255))
            WIN.blit(title, (WIDTH//2 - title.get_width()//2, 120))
            total_width = LIGHT_RADIUS * 2 * 5 + LIGHT_SPACING *4 
            start_x = WIDTH//2 - total_width//2
            y = 250

            for i in range(5):
                color = (255, 0, 0) if i < lights_on else(70, 70, 70)
                pygame.draw.circle(WIN, color, (start_x + i*(LIGHT_RADIUS*2 + LIGHT_SPACING), y),LIGHT_RADIUS)

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
    WIN.fill((20,20,20))
    text = pygame.font.SysFont("comicsans", 50).render("GO!", True, (255, 255, 255))     
    WIN.blit(text, (WIDTH//2-text.get_width()//2, 220))      
    pygame.display.update()
    pygame.time.wait(500)         

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

def handle_collision(player_car, Computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
            player_car.bounce()
    
    Computer_finish_poi_collide = Computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if Computer_finish_poi_collide != None:
            blit_text_center(WIN, MAIN_FONT, "You Lost!")
            pygame.display.update()
            pygame.time.wait(5000)
            game_info.reset()
            player_car.reset()
            Computer_car.reset()
    
    
    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            print(player_finish_poi_collide)
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            Computer_car.next_level(game_info.level)
            
def select_car(title_text, cars):
    selected = 0

    while True:
        WIN.fill((30,30,30))
        title = pygame.font.SysFont("comicsans", 40).render(title_text, True, (255, 255, 255))
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        mouse_pos = pygame.mouse.get_pos()

        for i, (name, image) in enumerate(cars):
            x = 120 + i * 170
            y = 180

            WIN.blit(image, (x, y))

            text = MAIN_FONT.render(name, True, (255, 255, 255))
            WIN.blit(text, (x, y + image.get_height() + 10))

            rect = pygame.Rect(
                x, y, image.get_width(), image.get_height()
            )

            if rect.collidepoint(mouse_pos):
                selected = i

            if i == selected:
                pygame.draw.rect(WIN, (255, 255, 0), rect.inflate(10, 10), 3)
        back_button.draw(WIN)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if back_button.clicked(event):
                BUTTON_SOUND.play()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, (name,image) in enumerate(cars):
                        x = 120 + i * 170
                        y = 180
                        rect = pygame.Rect(x,y,image.get_width(),image.get_height())
                        if rect.collidepoint(event.pos):
                            return cars[i][1]

def main_menu():
    while True:
        WIN.fill((20,20,20))
        title = pygame.font.SysFont("comicsans", 60).render("Formula 1 Style Racing Game", True, (255,255,255))
        WIN.blit(title,(WIDTH//2-title.get_width()//2, 100))
        play_button.draw(WIN)
        settings_button.draw(WIN)
        help_button.draw(WIN)
        quit_button.draw(WIN)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if play_button.clicked(event):
                BUTTON_SOUND.play()
                return
            if quit_button.clicked(event):
                BUTTON_SOUND.play()
                pygame.quit()
                sys.exit()
            if settings_button.clicked(event):
                BUTTON_SOUND.play()
                settings()
            if help_button.clicked(event):
                BUTTON_SOUND.play()
                howToPlay()
            if back_button.clicked(event):
                BUTTON_SOUND.play()
                return None

def settings():
    while True:
        WIN.fill((20,20,20))
        title = pygame.font.SysFont("comicsans", 60).render("Settings", True, (255,255,255))
        WIN.blit(title,(WIDTH//2-title.get_width()//2,60))
        music = MAIN_FONT.render("Music: On", True, (255,255,255))
        sfx = MAIN_FONT.render("Sound Effects: On", True, (255,255,255))
        WIN.blit(music,(120,180))
        WIN.blit(sfx,(120,230))
        back_button.draw(WIN)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if back_button.clicked(event):
                BUTTON_SOUND.play()
                return

def howToPlay():
    while True:
        WIN.fill((20,20,20))
        title = pygame.font.SysFont("comicsans", 55).render("How To Play", True,(255,255,255))
        WIN.blit(title,(WIDTH//2-title.get_width()//2,50))
        instructions = ["W - Accelerate", "S - Reverse", "A - Turn Left", "D - Turn Right", "Pause - ESC", "", "Reach the finish line before your opponent", "Avoid crashing into the barriers", "Each time you reach the finish line first the level will increase and so is" ,"the computer car's speed."]
        y = 150

        for line in instructions:
            text = MAIN_FONT.render(line, True, (255,255,255))
            WIN.blit(text,(100,y))
            y += 35
        back_button.draw(WIN)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if back_button.clicked(event):
                BUTTON_SOUND.play()
                return

def pause():
    
    while True:
        WIN.fill((20,20,20))

        title = pygame.font.SysFont("comicsans", 60).render("PAUSED", True, (255,255,255))
        WIN.blit(title, (WIDTH//2 - title.get_width()//2,100))

        resume_button.draw(WIN)
        menu_button.draw(WIN)
        Pause_quit_button.draw(WIN)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()   
            if resume_button.clicked(event):
                BUTTON_SOUND.play()
                return "resume"
            if menu_button.clicked(event):
                BUTTON_SOUND.play()
                return "menu"
            if Pause_quit_button.clicked(event):
                BUTTON_SOUND.play()
                pygame.quit()
                quit()

back_button = Button(30, HEIGHT - 70, 140, 50, "Back")
play_button = Button(WIDTH//2-150, 250, 300, 60, "Play")
settings_button = Button(WIDTH//2-150, 330, 300, 60, "Settings")
help_button = Button(WIDTH//2-150, 410, 300, 60, "How To Play")
quit_button = Button(WIDTH//2-150, 490, 300, 60, "QUIT")
resume_button = Button(WIDTH//2-150,250,300,60,"Resume")
menu_button = Button(WIDTH//2-150,340,300,60,"Main Menu")
Pause_quit_button = Button(WIDTH//2-150,430,300,60,"Quit")

clock = pygame.time.Clock()
images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))]

while True:
    main_menu()

    selected_car = select_car("Choose Your Car", CARS)
    if selected_car is None:
        continue

    available_opponents = []
    for name, image in CARS:
        if image != selected_car:
            available_opponents.append((name, image))

    selected_opponent = select_car("Choose Your Opponent", available_opponents)
    if selected_opponent is None:
        continue

    start_lights()
    player_car = PlayerCar(selected_car,3.5,4)
    Computer_car = ComputerCar(selected_opponent,1.5,4,PATH)
    game_info = GameInfo()

    run = True

    while run:
        clock.tick(FPS)
        draw(WIN,images,player_car,Computer_car,game_info)
        while not game_info.started:
            blit_text_center(WIN,MAIN_FONT,f"Press any key to start level {game_info.level}!")
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    choice = pause()
                    if choice == "resume":
                        continue
                    if choice == "menu":
                        run = False
                        break

        if not run:
            break

        move_player(player_car)
        Computer_car.move()
        handle_collision(player_car,Computer_car,game_info)

        if game_info.game_finished():
            blit_text_center(WIN, MAIN_FONT, "You won the game!")
            pygame.display.update()
            pygame.time.wait(5000)
            run = False

pygame.quit()
