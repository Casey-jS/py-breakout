import pygame as pg
import pygame.gfxdraw
import pygame.font
from pygame import mixer
import random as r
import os
import sys

fps = 60

# Breakout - Casey Sytsema
# background music and sound effects provided by freesound.com
# use a / d keys to move left / right
# press space to add a new ball in the game
# hitting the bottom of the screen will result in a loss of a life, but the ball will continue to move

# known bugs:  
# - occasionally the ball will get stuck inside of a block, cannot replicate the bug so I can't find the error
# - the ball hitting the side of the paddle will result in buggy collision
# - currently, removing a block shifts all other blocks in the row

# colors
white = (255,255,255)
black = (0,0,0)
pink = (255, 16, 240)
cyan = (0, 255, 255)

# screen and background info
screen_size = (640, 360)
window = pg.display.set_mode(screen_size)
pg.display.set_caption("Breakout")
bg = pg.transform.scale(pg.image.load(os.path.join("assets", "bg.png")), screen_size)


# object sizes
paddle_width = 200
block_size = (80, 30)
ball_radius = 12


class Game:
    def __init__(self):
        pg.init()
        self.__running = False
        self.clock = pg.time.Clock()
        self.paddle = Paddle()
        self.objects = pg.sprite.Group()
        for _ in range(40): # create all blocks
            block = Block()
            block.color()
            self.objects.add(block)
        self.ball = Ball()
        self.paddle_group = pg.sprite.Group()
        self.paddle_group.add(self.paddle)
        self.__score = 0
        self.__lives = 3
        self.ball2 = Ball()
        self.__ball_added = False

        mixer.init()
        mixer.music.load('assets/bg.mp3')
        self.ping = pg.mixer.Sound('assets/ping.wav')
        mixer.music.play()

    # hideous method for placing the blocks on the screen    
    def place_blocks(self):
        x, y, i = 0, 0, 0
        for block in self.objects:  
            if i % 8 == 0 and i != 0:
                y += 30
                x = 0
            block.rect.x = x
            block.rect.y = y
            block.draw(window, x, y)
            x += 80
            i += 1
    def set_lives(self, lives):
        self.__lives = lives
    def get_lives(self):
        return self.__lives
    def set_lives(self, score):
        self.__score = score
    
    def show_stats(self):
        font = pg.font.SysFont('Arial', 20)
        lives = font.render("Lives: " + str(self.__lives), False, cyan)
        score = font.render("Score: " + str(self.__score), False, cyan)
        window.blit(lives, (10, 5))
        window.blit(score, (10, 30))

    def add_ball(self):
        self.__ball_added = True
    
    def game_over(self):
        running = True
        print("game over hit")

        while running:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    running = False
                    pg.quit()
                    exit()
            bg = pg.transform.scale(pg.image.load(os.path.join("assets", "game-over.jpg")), screen_size)
            window.blit(bg, (0,0))
            pg.display.update()
            

    def run(self):
        while self.__running:
            if self.__lives == 0:
                self.__running = False
                self.game_over()
            events = pg.event.get()
            for event in events:
                if event.type == pg.KEYDOWN and not self.__ball_added: # add ball with spacebar
                    if event.key == pg.K_SPACE:
                        self.add_ball()

                if event.type == pg.QUIT: # if user wants to exit
                    self.__running = False
                    pg.quit()
                    exit()
            self.paddle.move() # check input for paddle movement
            self.ball.move()
            self.__lives = 3 - self.ball.oobcount
                
            if self.__ball_added:
                self.ball2.move()
            if self.ball.check_paddle_collisions(self.paddle_group):
                mixer.Sound.play(self.ping)
            
            block_hit = self.ball.check_block_collisions(self.objects)
            if block_hit != None:
                if block_hit.hit():
                    self.__score += 1
                mixer.Sound.play(self.ping)
            
            if self.__ball_added:
                if self.ball2.check_paddle_collisions(self.paddle_group):
                    mixer.Sound.play(self.ping)
                block_hit = self.ball2.check_block_collisions(self.objects)
                if block_hit != None:
                    block_hit.hit()
                    mixer.Sound.play(self.ping)


            window.blit(bg, (0,0)) # draw background
            self.paddle.draw(window) # draw paddle
            self.ball.draw(window) 
            if self.__ball_added:
                self.ball2.draw(window)
            self.place_blocks() # draw blocks
            self.show_stats()
            pg.display.update() # update display
            self.clock.tick(fps) # tick clock
            

    def set_running(self, status): self.__running = status
    
class Paddle(pg.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.image = pg.Surface( (paddle_width, 10) )
        self.image.fill(pink)
        self.rect = self.image.get_rect()
        self.rect.x = screen_size[0] // 2 
        self.rect.y = screen_size[1] - 25
        self.__velocity = 8
    
    def draw(self, surface): surface.blit(self.image, (self.rect.x, self.rect.y))
    
    def move(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            if self.rect.x < 0: # if the paddle leaves the left side of the screen
                return
            self.rect.x -= self.__velocity
        if keys[pg.K_d]:
            if self.rect.x > screen_size[0] - paddle_width:
                return
            self.rect.x += self.__velocity

class Block(pg.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.image = pg.Surface(block_size)
        self.rect = self.image.get_rect()
        self.__health = 0
        self.rect.x = 0
        self.rect.y = 0
    
    def set_health(self, hp):
        self.__health = hp
    
    def get_health(self):
        return self.__health

    def hit(self):
        self.__health -= 25
        if self.__health <= 0:
            self.kill()
            return True
    # assigns a color to the block,
    # colors it, and sets health
    def color(self):
        color = r.randint
        red = color(0,255)
        green = color(0,255)
        blue = color(0,255)
        self.image.fill((red, green, blue))
        health = 766 - (red + blue + green)
        self.set_health(health)
    
    def draw(self, surface, x, y):
        surface.blit(self.image, (x,y))
        
class Ball(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.ball_img = pg.Surface((29, 29), pg.SRCALPHA)
        pg.gfxdraw.aacircle(self.ball_img, ball_radius, ball_radius, 10, cyan)
        pg.gfxdraw.filled_circle(self.ball_img, ball_radius, ball_radius, 10, cyan)
        self.__image = self.ball_img
        self.rect = self.__image.get_rect()
        self.__yvelocity = 5
        self.__xvelocity = 5
        self.rect.x = 320
        self.rect.y = 300
        self.oobcount = 0
    
    def draw(self, surface):
        surface.blit(self.__image, (self.rect.x, self.rect.y))
    
    def move(self): 
        if self.rect.x <= 0: self.__xvelocity *= -1 # if the ball hits the left side of the screen
        if self.rect.x >= screen_size[0]: self.__xvelocity *= -1 # if the ball hits right side of screen
        if self.rect.y <= 0: self.__yvelocity *= -1 # if ball hits top of screen
        if self.rect.y >= screen_size[1]: # if ball hits bottom of screen, increase out of bounds count
            self.__yvelocity *= -1
            self.oobcount += 1
            
        self.rect.x += self.__xvelocity
        self.rect.y += self.__yvelocity

    def check_paddle_collisions(self, paddle):
        if pg.sprite.spritecollideany(self, paddle):
            self.__yvelocity *= -1
            return True
    
    def check_block_collisions(self, blocks):
        block_hit = pg.sprite.spritecollideany(self, blocks)
        
        if block_hit != None:
            ball_right = self.rect.right
            ball_left = self.rect.left
            block_right = block_hit.rect.right
            block_left = block_hit.rect.left
            ball_top = self.rect.top
            block_bottom = block_hit.rect.bottom

            # for bouncing left / right
            if (ball_left + 5 == block_right or ball_right - 5 == block_left) and ball_top + 5 != block_bottom:
                self.__xvelocity *= -1
            else:
                self.__yvelocity *= -1
            return block_hit
        return None
                      
def main():
    game = Game()
    game.set_running(True)
    game.run()


if __name__ == '__main__':
    main()

