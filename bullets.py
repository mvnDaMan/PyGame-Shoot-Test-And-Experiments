# http://programarcadegames.com/python_examples/show_file.php?file=game_class_example.py
import pygame
import random
import math

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500


class Block(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([20, 20])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.hp = 10

    def reset_pos(self):
        self.rect.y = random.randrange(-300, -20)
        self.rect.x = random.randrange(SCREEN_WIDTH)

    def update(self):
        self.rect.y += 1
        if self.rect.y > SCREEN_HEIGHT + self.rect.height:
            self.reset_pos()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([20, 20])
        self.image.fill(RED)
        self.rect = self.image.get_rect()

        self.arm_cap = 1
        self.arm_rate = 1
        self.arm_progress = self.arm_cap    # set to armed

    def update(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([4, 10])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage = 3

    def update(self):
        self.rect.y -= 4


class WeirdBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.Surface((4, 4))
        self.image.fill((0, random.randrange(128, 256), random.randrange(0, 256)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.center_x = x
        self.angle = 0
        self.angle_delta = random.randrange(-100, 100) / 500
        self.radius = random.randrange(0, 100)
        self.damage = 1

    def update(self):
        self.rect.y -= 10
        self.rect.x = self.center_x + self.radius * math.sin(self.angle)
        self.angle += self.angle_delta


class CrazyBullet(WeirdBullet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.center_y = y
        self.damage = 1
        # self.radius *= 2
        self.radius = 30
        self.current_radius = 0

    def update(self):
        # self.center_y -= 1
        mouse_pos = pygame.mouse.get_pos()
        self.center_x = mouse_pos[0]
        self.center_y = mouse_pos[1]

        self.rect.x = self.center_x + self.current_radius * math.sin(self.angle)
        self.rect.y = self.center_y + self.current_radius * math.cos(self.angle)
        self.angle += self.angle_delta

        if self.current_radius < self.radius:
            # self.current_radius += self.angle_delta * 3   # spiral endlessly since angle_delta increments slowly
            self.current_radius += 0.1


class Game(object):
    def __init__(self):
        self.score = 0
        self.game_over = False
        self.block_list = pygame.sprite.Group()
        self.bullets_list = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.font = pygame.font.SysFont("Impact", 20)

        for i in range(100):
            block = Block()
            block.rect.x = random.randrange(SCREEN_WIDTH)
            block.rect.y = random.randrange(-300, SCREEN_HEIGHT)
            self.block_list.add(block)
            self.all_sprites_list.add(block)

        self.player = Player()
        self.all_sprites_list.add(self.player)
        self.player_firing = False

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.__init__()
                else:
                    if not self.player_firing:
                        self.player_firing = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.player_firing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    s_bullet = WeirdBullet(self.player.rect.x, self.player.rect.y)
                    self.all_sprites_list.add(s_bullet)
                    self.bullets_list.add(s_bullet)

    def run_logic(self):
        if not self.game_over:
            self.all_sprites_list.update()
            blocks_hit_list = pygame.sprite.spritecollide(self.player, self.block_list, True)

            for block in blocks_hit_list:
                self.score += 1
                print(self.score)

            if self.player.arm_progress < self.player.arm_cap:
                self.player.arm_progress += self.player.arm_rate

            if self.player_firing:
                if self.player.arm_progress >= self.player.arm_cap:
                    bullet_x = self.player.rect.x + (self.player.rect.width / 2) - 2

                    bullet = WeirdBullet(bullet_x, self.player.rect.y)
                    self.bullets_list.add(bullet)
                    self.all_sprites_list.add(bullet)

                    bullet2 = CrazyBullet(bullet_x, self.player.rect.y)
                    self.bullets_list.add(bullet2)
                    self.all_sprites_list.add(bullet2)

                    self.player.arm_progress = 0
                    # print("Pew")

            for bullet in self.bullets_list:
                if bullet.rect.y + bullet.rect.height < 0:
                    self.all_sprites_list.remove(bullet)
                    self.bullets_list.remove(bullet)
                    continue

                for block in self.block_list:
                    if pygame.sprite.collide_rect(block, bullet):
                        block.hp -= bullet.damage
                        block.rect.y -= 5

                        self.bullets_list.remove(bullet)
                        self.all_sprites_list.remove(bullet)

                        if (block.hp <= 0):
                            self.block_list.remove(block)
                            self.all_sprites_list.remove(block)
                            self.score += 5
                        # print("collide")

            if len(self.block_list) == 0:
                self.game_over = True

    def display_frame(self, screen):
        screen.fill(BLACK)

        if self.game_over:
            # font = pygame.font.SysFont("serif", 25)
            text = self.font.render("Game Over, click to restart", True, RED)
            center_x = (SCREEN_WIDTH - text.get_width()) / 2
            center_y = (SCREEN_HEIGHT - text.get_height()) / 2
            screen.blit(text, (center_x, center_y))
        else:
            self.all_sprites_list.draw(screen)

        score_text = self.font.render("Score: {0}".format(self.score), True, GREEN)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()


def main():
    pygame.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Game Class")
    pygame.mouse.set_visible(False)

    done = False
    clock = pygame.time.Clock()

    game = Game()

    while not done:
        done = game.process_events()
        game.run_logic()
        game.display_frame(screen)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()