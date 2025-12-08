#  make a top down map with a moveable player using pygame
import pygame
import sys
import random
from sys import exit
from pygame.locals import QUIT
import math
import colorsys





pygame.init()     
# create window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Photon Edge")
clock = pygame.time.Clock()
background = pygame.image.load("background.png").convert()


def shift_hue(surface, hue_shift):
    """Shift the hue of a surface by the given amount (0-360 degrees)"""
    # Convert hue shift to 0-1 range
    hue_shift = hue_shift / 360.0
    
    # Lock the surface for pixel access
    surface.lock()
    
    # Create a copy to modify
    result = surface.copy()
    result.lock()
    
    # Get the color at each pixel and shift its hue
    for y in range(result.get_height()):
        for x in range(result.get_width()):
            color = result.get_at((x, y))
            
            # Skip transparent pixels
            if color.a == 0:
                continue
            
            r = color.r / 255.0
            g = color.g / 255.0
            b = color.b / 255.0
            a = color.a
            
            # Convert RGB to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Shift hue
            h = (h + hue_shift) % 1.0
            
            # Convert back to RGB
            new_r, new_g, new_b = colorsys.hsv_to_rgb(h, s, v)
            
            new_color = (int(new_r * 255), int(new_g * 255), int(new_b * 255), a)
            result.set_at((x, y), new_color)
    
    result.unlock()
    surface.unlock()
    
    return result


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 0, 0))  # Transparent
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(400, 300)
        self.image = pygame.image.load("player.png").convert_alpha()
        # Scale the image 1.25x bigger
        original_size = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(original_size[0] * 1.25), int(original_size[1] * 1.25)))
        self.base_image = self.image
        self.hitbox = self.image.get_rect(center = self.pos)
        self.rect = self.hitbox.copy()
        self.speed = 2.5
        self.swordbeam_cooldown = 0
        self.swordbeam = False
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.health = 100
        self.damage_cooldown = 0
        self.beam_size_multiplier = 1.0  # 1.0 = normal size, 1.5 = 50% larger

    def player_rotate(self):
        # Rotate based on movement direction from WASD
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.angle = math.degrees(math.atan2(-self.velocity_y, self.velocity_x))
        # If no movement, keep current angle
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.hitbox.center)
    
    def user_input(self):
        self.velocity_x = 0
        self.velocity_y = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
            self.velocity_x = 0
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
            self.velocity_x = 0
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.velocity_y = 0
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.velocity_y = 0

        if pygame.mouse.get_pressed() == (1, 0, 0):
            if self.swordbeam_cooldown == 0:
                self.create_swordbeam()
    
    def create_swordbeam(self):
        if self.swordbeam_cooldown == 0:
            self.swordbeam_cooldown = 50
            self.beam = PlayerBeam(self.hitbox.centerx, self.hitbox.centery, self.angle)
            all_sprites.add(self.beam)
            player_beam_group.add(self.beam)

    def move(self):
        self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        if pygame.sprite.spritecollide(self, wall_group, False):
            # Undo vertical movement
            self.pos.y -= self.velocity_y
            self.hitbox.center = (round(self.pos.x), round(self.pos.y))
        
        self.rect.center = self.hitbox.center
    
    def check_damage(self):
        # Check if hit by enemy beams
        hit_beams = pygame.sprite.spritecollide(self, enemy_beam_group, True)
        if hit_beams and self.damage_cooldown <= 0:
            self.health -= 10
            self.damage_cooldown = 30  # Invincibility frame of 30 frames
    
    def update(self):
        self.user_input()
        self.move()
        self.check_damage()
        self.player_rotate()
        if self.swordbeam_cooldown > 0:
            self.swordbeam_cooldown -= 1
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(enemy_group, all_sprites)
        self.base_image = pygame.image.load("enemy1.png").convert_alpha()
        self.base_image = pygame.transform.rotozoom(self.base_image, 0, 1.5)
        self.image = self.base_image
        self.position = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(center=self.position)
        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = 2
        self.shoot_cooldown = 0
        self.shoot_interval = 60  # Shoot every 60 frames (1 second at 60 FPS)
        self.angle = 0

    def chasing(self):
        # Calculate direction to player
        player_vector = pygame.math.Vector2(player1.rect.center)
        distance_vector = player_vector - self.position
        
        # Determine which direction is closest to the player (up, down, left, right)
        abs_x = abs(distance_vector.x)
        abs_y = abs(distance_vector.y)
        
        if abs_x > abs_y:
            # Move left or right
            if distance_vector.x > 0:
                self.direction = pygame.math.Vector2(1, 0)  # Right
                self.angle = 0
            else:
                self.direction = pygame.math.Vector2(-1, 0)  # Left
                self.angle = 180
        else:
            # Move up or down
            if distance_vector.y > 0:
                self.direction = pygame.math.Vector2(0, 1)  # Down
                self.angle = -90
            else:
                self.direction = pygame.math.Vector2(0, -1)  # Up
                self.angle = 90
        
        self.velocity = self.direction * self.speed
        self.position += self.velocity
        self.rect.center = self.position
        
        # Rotate sprite based on direction
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)

    def shoot(self):
        # Calculate direction toward player and constrain to 4 directions
        player_vector = pygame.math.Vector2(player1.rect.center)
        distance_vector = player_vector - self.position
        
        # Determine which direction is closest (up, down, left, right)
        abs_x = abs(distance_vector.x)
        abs_y = abs(distance_vector.y)
        
        if abs_x > abs_y:
            # Shoot left or right
            if distance_vector.x > 0:
                angle = 0  # Right
            else:
                angle = 180  # Left
        else:
            # Shoot up or down
            if distance_vector.y > 0:
                angle = -90  # Down
            else:
                angle = 90  # Up
        
        # Create beam
        beam = EnemyBeam(self.position.x, self.position.y, angle)
        all_sprites.add(beam)
        enemy_beam_group.add(beam)

    def update(self):
        self.chasing()
        
        # Check if hit by player beam
        hit_beams = pygame.sprite.spritecollide(self, player_beam_group, False)
        for beam in hit_beams:
            beam.kill()
            # Increment enemy kill counter
            global enemy_kills
            enemy_kills += 1
            # Drop item when enemy dies (25% chance for PowerUp, 75% for Healing)
            if random.random() < 0.25:
                item = PowerUp(self.position.x, self.position.y)
            else:
                item = HealingItem(self.position.x, self.position.y)
            all_sprites.add(item)
            item_group.add(item)
            self.kill()
            return
        
        # Handle shooting
        if self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = self.shoot_interval
        else:
            self.shoot_cooldown -= 1


class StrongEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(enemy_group, all_sprites)
        self.base_image = pygame.image.load("enemy2.png").convert_alpha()
        self.base_image = pygame.transform.rotozoom(self.base_image, 0, 3.0)
        self.image = self.base_image
        self.position = pygame.math.Vector2(pos)
        self.rect = self.image.get_rect(center=self.position)
        self.direction = pygame.math.Vector2()
        self.velocity = pygame.math.Vector2()
        self.speed = 1.5  # Slightly slower than regular enemy
        self.shoot_cooldown = 0
        self.shoot_interval = 60  # Shoot every 60 frames (1 second at 60 FPS)
        self.angle = 0
        self.health = 3  # Takes 3 hits to kill

    def chasing(self):
        # Calculate direction to player
        player_vector = pygame.math.Vector2(player1.rect.center)
        distance_vector = player_vector - self.position
        
        # Determine which direction is closest to the player (up, down, left, right)
        abs_x = abs(distance_vector.x)
        abs_y = abs(distance_vector.y)
        
        if abs_x > abs_y:
            # Move left or right
            if distance_vector.x > 0:
                self.direction = pygame.math.Vector2(1, 0)  # Right
                self.angle = 0
            else:
                self.direction = pygame.math.Vector2(-1, 0)  # Left
                self.angle = 180
        else:
            # Move up or down
            if distance_vector.y > 0:
                self.direction = pygame.math.Vector2(0, 1)  # Down
                self.angle = -90
            else:
                self.direction = pygame.math.Vector2(0, -1)  # Up
                self.angle = 90
        
        self.velocity = self.direction * self.speed
        self.position += self.velocity
        self.rect.center = self.position
        
        # Rotate sprite based on direction
        self.image = pygame.transform.rotate(self.base_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)

    def shoot(self):
        # Calculate direction toward player and constrain to 4 directions
        player_vector = pygame.math.Vector2(player1.rect.center)
        distance_vector = player_vector - self.position
        
        # Determine which direction is closest (up, down, left, right)
        abs_x = abs(distance_vector.x)
        abs_y = abs(distance_vector.y)
        
        if abs_x > abs_y:
            # Shoot left or right
            if distance_vector.x > 0:
                angle = 0  # Right
            else:
                angle = 180  # Left
        else:
            # Shoot up or down
            if distance_vector.y > 0:
                angle = -90  # Down
            else:
                angle = 90  # Up
        
        # Create 2x size beam
        beam = StrongEnemyBeam(self.position.x, self.position.y, angle)
        all_sprites.add(beam)
        enemy_beam_group.add(beam)

    def update(self):
        self.chasing()
        
        # Check if hit by player beam
        hit_beams = pygame.sprite.spritecollide(self, player_beam_group, False)
        for beam in hit_beams:
            beam.kill()
            self.health -= 1
            if self.health <= 0:
                # Drop item when enemy dies (25% chance for PowerUp, 75% for Healing)
                global enemy_kills
                enemy_kills += 1
                if random.random() < 0.25:
                    item = PowerUp(self.position.x, self.position.y)
                else:
                    item = HealingItem(self.position.x, self.position.y)
                all_sprites.add(item)
                item_group.add(item)
                self.kill()
            return
        
        # Handle shooting
        if self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = self.shoot_interval
        else:
            self.shoot_cooldown -= 1


class HealingItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a simple green healing item (circle)
        self.image = pygame.image.load("Health.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position = pygame.math.Vector2(x, y)
        self.heal_amount = 50
    
    def update(self):
        # Check if player picks up the item
        if pygame.sprite.spritecollide(self, [player1], False):
            player1.health = min(player1.health + self.heal_amount, 200)  # Cap at 200
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("Sword powerup.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.position = pygame.math.Vector2(x, y)
        self.duration = 300  # Duration in frames (5 seconds at 60 FPS)
    
    def update(self):
        # Check if player picks up the item
        if pygame.sprite.spritecollide(self, [player1], False):
            player1.beam_size_multiplier *= 1.5  # Multiply by 1.5x each pickup
            self.kill()

class PlayerBeam(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.spritesheet = pygame.image.load("Beam.png").convert_alpha()
        self.angle = angle
        self.frame = 0
        self.animation_speed = 0.15
        self.frame_width = 32
        self.frame_height = 32
        # Calculate number of frames in sprite sheet
        self.num_frames = self.spritesheet.get_width() // self.frame_width
        # Get the current beam size multiplier from the player
        self.size_multiplier = player1.beam_size_multiplier if hasattr(player1, 'beam_size_multiplier') else 1.0
        self.update_image()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        self.speed = 10
        self.velocity = pygame.math.Vector2(self.speed, 0).rotate(-self.angle)
    
    def update_image(self):
        # Extract frame from spritesheet
        frame_x = int(self.frame % self.num_frames) * self.frame_width
        frame_y = 0
        frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        frame_image = self.spritesheet.subsurface(frame_rect).copy()
        # Scale up 2x and by the multiplier before rotating
        scale = int(self.frame_width * 2 * self.size_multiplier), int(self.frame_height * 2 * self.size_multiplier)
        frame_image = pygame.transform.scale(frame_image, scale)
        # Rotate the frame
        self.image = pygame.transform.rotate(frame_image, self.angle)
    
    def beam_movement(self):
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.rect.center = (int(self.x), int(self.y))
        
        # Despawn if off-screen
        if self.rect.right < 0 or self.rect.left > 800 or self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()
            return
        
        # Animate frames (loops automatically with modulo)
        self.frame += self.animation_speed
        self.update_image()

    def update(self):
        self.beam_movement()


class EnemyBeam(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.spritesheet = pygame.image.load("Beam.png").convert_alpha()
        self.angle = angle
        self.frame = 0
        self.animation_speed = 0.15
        self.frame_width = 32
        self.frame_height = 32
        # Calculate number of frames in sprite sheet
        self.num_frames = self.spritesheet.get_width() // self.frame_width
        self.update_image()
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        self.speed = 10
        self.velocity = pygame.math.Vector2(self.speed, 0).rotate(-self.angle)
        self.damage = 10  # Default damage for enemy beams
    
    def update_image(self):
        # Extract frame from spritesheet
        frame_x = int(self.frame % self.num_frames) * self.frame_width
        frame_y = 0
        frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        frame_image = self.spritesheet.subsurface(frame_rect).copy()
        # Scale up 2x before rotating
        frame_image = pygame.transform.scale(frame_image, (self.frame_width * 2, self.frame_height * 2))
        # Apply hue shift (shift by 120 degrees for a cyan/teal color)
        frame_image = shift_hue(frame_image, 120)
        # Rotate the frame
        self.image = pygame.transform.rotate(frame_image, self.angle)
    
    def beam_movement(self):
        self.x += self.velocity.x
        self.y += self.velocity.y
        self.rect.center = (int(self.x), int(self.y))
        
        # Animate frames (loops automatically with modulo)
        self.frame += self.animation_speed
        self.update_image()

    def update(self):
        self.beam_movement()
        # Despawn if off-screen
        if self.rect.right < 0 or self.rect.left > 800 or self.rect.bottom < 0 or self.rect.top > 600:
            self.kill()

class StrongEnemyBeam(EnemyBeam):
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle)
        self.damage = 15  # Stronger beam

    def update_image(self):
        frame_x = int(self.frame % self.num_frames) * self.frame_width
        frame_y = 0
        frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        frame_image = self.spritesheet.subsurface(frame_rect).copy()
        frame_image = pygame.transform.scale(frame_image, (self.frame_width * 2, self.frame_height * 2))
        frame_image = shift_hue(frame_image, 120)
        # 2x larger
        frame_image = pygame.transform.scale(frame_image, (frame_image.get_width()*2, frame_image.get_height()*2))
        self.image = pygame.transform.rotate(frame_image, self.angle)

class BossBeam(EnemyBeam):
    def __init__(self, x, y, angle):
        super().__init__(x, y, angle)
        self.damage = 20  # Boss beam deals double damage

    def update_image(self):
        frame_x = int(self.frame % self.num_frames) * self.frame_width
        frame_y = 0
        frame_rect = pygame.Rect(frame_x, frame_y, self.frame_width, self.frame_height)
        frame_image = self.spritesheet.subsurface(frame_rect).copy()
        frame_image = pygame.transform.scale(frame_image, (self.frame_width * 2, self.frame_height * 2))
        frame_image = shift_hue(frame_image, 120)
        # 4x larger
        frame_image = pygame.transform.scale(frame_image, (frame_image.get_width()*4, frame_image.get_height()*4))
        self.image = pygame.transform.rotate(frame_image, self.angle)

class BossEnemy(StrongEnemy):
    def __init__(self, pos):
        super().__init__(pos)
        self.base_image = pygame.image.load("enemy3.png").convert_alpha()
        self.base_image = pygame.transform.rotozoom(self.base_image, 0, 12.0)  # 4x larger than StrongEnemy (3.0)
        self.image = self.base_image
        self.rect = self.image.get_rect(center=self.position)
        self.health = 10
        self.shoot_interval = 40  # Shoots more frequently

    def shoot(self):
        player_vector = pygame.math.Vector2(player1.rect.center)
        distance_vector = player_vector - self.position
        abs_x = abs(distance_vector.x)
        abs_y = abs(distance_vector.y)
        if abs_x > abs_y:
            if distance_vector.x > 0:
                angle = 0
            else:
                angle = 180
        else:
            if distance_vector.y > 0:
                angle = -90
            else:
                angle = 90
        beam = BossBeam(self.position.x, self.position.y, angle)
        all_sprites.add(beam)
        enemy_beam_group.add(beam)

all_sprites = pygame.sprite.Group()
player_beam_group = pygame.sprite.Group()
enemy_beam_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()
player1 = Player()
# Create enemy at random position (avoiding the edges)
enemy_x = random.randint(50, 750)
enemy_y = random.randint(50, 550)
badguy = Enemy((enemy_x, enemy_y))

# Enemy spawn timer
enemy_spawn_timer = 0
enemy_spawn_interval = 300  # 600 frames = 10 seconds at 60 FPS

# Enemy kill counter for difficulty scaling
enemy_kills = 0

all_sprites.add(player1)

def spawn_enemy():
    """Spawn a new enemy at a random position"""
    enemy_x = random.randint(50, 750)
    enemy_y = random.randint(50, 550)
    # Spawn StrongEnemy after killing 5 enemies, otherwise spawn regular Enemy
    if enemy_kills >= 5:
        new_enemy = StrongEnemy((enemy_x, enemy_y))
    else:
        new_enemy = Enemy((enemy_x, enemy_y))
    enemy_group.add(new_enemy)
    all_sprites.add(new_enemy)

# Create walls around the edges
walls = [
    Wall(0, 0, 800, 20),      # Top wall
    Wall(0, 580, 800, 20),    # Bottom wall
    Wall(0, 0, 20, 600),      # Left wall
    Wall(780, 0, 20, 600),    # Right wall
]

for wall in walls:
    wall_group.add(wall)


game_started = False
game_over = False

# Boss spawn logic
boss_spawned = False
boss = None
boss_health_bar_font = pygame.font.Font(None, 36)
strong_enemy_kills = 0

# In StrongEnemy's update, increment strong_enemy_kills when killed
StrongEnemy_update_original = StrongEnemy.update

def StrongEnemy_update_with_kill(self):
    StrongEnemy_update_original(self)
    if not self.alive():
        global strong_enemy_kills
        strong_enemy_kills += 1
StrongEnemy.update = StrongEnemy_update_with_kill

win_screen = False

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_started:
                    game_started = True
            if event.key == pygame.K_ESCAPE:
                if win_screen:
                    pygame.quit()
                    sys.exit()
    
    if not game_started:
        # Display start screen
        screen.fill((0, 0, 0))
        font_large = pygame.font.Font(None, 72)
        start_text = font_large.render("PRESS SPACE TO START", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=(400, 300))
        screen.blit(start_text, text_rect)
    elif game_over:
        # Display game over screen
        screen.fill((0, 0, 0))
        font_large = pygame.font.Font(None, 72)
        game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(400, 300))
        screen.blit(game_over_text, text_rect)
    else:
        screen.blit(background, (0, 0))
        screen.blit(player1.image, player1.rect)
        
        player1.update()
        pygame.draw.rect(screen, (255, 0, 0), player1.hitbox, 2)
        all_sprites.draw(screen)
        all_sprites.update()
        
        # Spawn timer logic
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_interval:
            spawn_enemy()
            enemy_spawn_timer = 0
        
        # Check for game over
        if player1.health <= 0:
            game_over = True
        
        # Display health bar at the top
        bar_x, bar_y = 10, 10
        bar_width, bar_height = 200, 24
        health_ratio = min(player1.health / 200, 1.0)
        # Draw background bar
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Draw health amount
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        # Optional: draw border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Boss spawn logic
    if strong_enemy_kills >= 5 and not boss_spawned:
        boss = BossEnemy((400, 150))
        enemy_group.add(boss)
        all_sprites.add(boss)
        boss_spawned = True

    # Draw boss health bar if boss is alive
    if boss_spawned and boss and boss.alive():
        bar_width = 400
        bar_height = 24
        health_ratio = boss.health / 10
        pygame.draw.rect(screen, (60, 60, 60), (200, 50, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (200, 50, int(bar_width * health_ratio), bar_height))
        text = boss_health_bar_font.render("BOSS", True, (255, 255, 255))
        screen.blit(text, (200, 50 - 32))

    # Boss beam deals double damage to player
    for sprite in enemy_beam_group:
        if isinstance(sprite, BossBeam) and player1.rect.colliderect(sprite.rect):
            player1.health -= sprite.damage
            sprite.kill()

    # WIN SCREEN: If boss is defeated
    if boss_spawned and boss and not boss.alive():
        win_screen = True

    if win_screen:
        screen.fill((0, 0, 0))
        font_large = pygame.font.Font(None, 72)
        win_text = font_large.render("YOU WIN!", True, (0, 255, 0))
        text_rect = win_text.get_rect(center=(400, 250))
        screen.blit(win_text, text_rect)
        font_small = pygame.font.Font(None, 48)
        esc_text = font_small.render("Press ESC to exit", True, (255, 255, 255))
        esc_rect = esc_text.get_rect(center=(400, 350))
        screen.blit(esc_text, esc_rect)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        pygame.display.update()
        clock.tick(60)
        continue

    pygame.display.update()
    clock.tick(60)