import pygame
from config import *
import random


sprite = pygame.sprite.Sprite

class DifficultyManager(Serializable):
    def __init__(self):
        self.elapsed_time = 0.0
        self.stage = 0
        self.interval = 60.0  # 5 minutes
        self.scale = 1.1       # 10%

    def draw(self):
        # Positioning
        x, y = SC_W//2 - 100, 10
        width, height = 200, 50

        # Draw background container
        time_container = Container(x=x, y=y, width=width, height=height, color=DESERT)
        time_container.draw_rect(SCREEN)

        # Fonts
        font = pygame.font.Font(FONT_PATH, 36)

        # Convert elapsed time to MM:SS
        total_seconds = int(self.elapsed_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = f"{minutes:02d}:{seconds:02d}"

        # Render text
        text_surface = font.render(time_text, True, BLACK)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        SCREEN.blit(text_surface, text_rect)

        # Optional: show difficulty level
        level_surface = font.render(f"Stage {self.stage}", True, BLACK)
        level_rect = level_surface.get_rect(midtop=(x + width // 2, y + height + 5))
        SCREEN.blit(level_surface, level_rect)


    def update(self, dt):
        self.elapsed_time += dt
        if self.elapsed_time >= self.interval:
            self.elapsed_time -= self.interval
            self.stage += 1

    def multiplier(self):
        return self.scale ** self.stage

class Button:
    def __init__(self, x, y, width, height, text, color, text_color, action=None, 
                 border_color=BLACK, border_size=3, font_size = 48):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.text_color = text_color
        self.action = action
        self.border_color = border_color
        self.border_size = border_size
        self.font_path = FONT_PATH
        self.font_size = font_size  # Font size

    def draw(self, hover=False):
        color = (255, 50, 50) if hover else self.color
        # Draw border (slightly bigger rectangle)
        pygame.draw.rect(SCREEN, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)

        # Draw actual button
        pygame.draw.rect(SCREEN, color, self.rect, border_radius=8)

        # Load font (custom or default)
        font = pygame.font.Font(self.font_path, self.font_size) if self.font_path else pygame.font.Font(None, self.font_size)
        
        # Render text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        SCREEN.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        print("is_clicked")
        return self.rect.collidepoint(pos)


class Container:
    def __init__(self, x, y, width, height, color, border_color=BLACK, border_size=3):
        self.posx, self.posy = x, y
        self.width, self.height = width, height
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.border_color = border_color
        self.border_size = border_size

    def draw_rect(self, hover=False):
        # color = (255, 50, 50) if hover else self.color
        pygame.draw.rect(SCREEN, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)
        pygame.draw.rect(SCREEN, self.color, self.rect, border_radius=8)

    def draw_circle(self, camera_offset, center_x, center_y):
        pygame.draw.circle(SCREEN, (255, 255, 255), (int(center_x), int(center_y)), WORLD_RADIUS)
        pygame.draw.circle(SCREEN, (255, 0, 0), (int(center_x), int(center_y)), WORLD_RADIUS, 5)

    def draw_opaque(self, snapshot):
        SCREEN.blit(snapshot, (0, 0))
        # Create transparent overlay surface
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Fill with color (RGBA) — make sure self.color has 4 values
        overlay.fill(self.color)

        # Draw border if needed
        pygame.draw.rect(SCREEN, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)

        # Blit overlay with transparency
        SCREEN.blit(overlay, (self.posx, self.posy))

class Bullet(Serializable):
    def __init__(self, x, y, target, dmg):
        self.pos = pygame.Vector2(x, y)
        self.speed = 400
        self.radius = 4
        self.dmg=dmg

        direction = pygame.Vector2(target) - self.pos
        self.vel = direction.normalize() * self.speed

        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)


    def update(self, dt):
        self.pos += self.vel * dt
        self.rect.x = int(self.pos.x - self.radius)
        self.rect.y = int(self.pos.y - self.radius)

    def draw(self, camera):
        posx = int(self.pos.x - camera.offset_x)
        posy = int(self.pos.y - camera.offset_y)
        pygame.draw.circle(SCREEN, (255, 50, 50), (posx, posy), self.radius)


        
# class Carriage():
#     def __init__(self, x, y, width, height, color, border_color, border_size):
#         # === Stats ===
#         self.pos = pygame.Vector2(x, y)
#         self.max_hp = 100
#         self.hp = max(0, self.max_hp)
#         self.armor = 0

#         # === Object ===
#         self.rect = pygame.Rect(self.pos.x, self.pos.y, width, height)
#         self.color = color
#         self.border_color = border_color
#         self.border_size = border_size

#     def draw(self, camera):
#         posx = int(self.pos.x - camera.offset_x)
#         posy = int(self.pos.y - camera.offset_y)
#         pygame.draw.rect(SCREEN, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)
#         pygame.draw.rect(SCREEN, self.color, (posx, posy), border_radius=8)

#         font = pygame.font.Font(FONT_PATH, 20)
#         hp_txt = f"{self.hp}/{self.max_hp}"
#         text_surface = font.render(hp_txt, True, BLACK)
#         text_rect = text_surface.get_rect(
#         center=(self.rect.centerx, self.rect.bottom + 20)
#         )
#         SCREEN.blit(text_surface, text_rect)

#     def take_dmg(self, dmg):
#         self.hp -= dmg
#         if self.hp <= 0:
#             self.destroyed = True



class Player(Serializable):
    def __init__(self, x, y, width, height, color, border_color, border_size):
        # === Objects ===
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, width, height)
   
        self.color = color
        self.border_color = border_color
        self.border_size = border_size

        # === Stats ===
        self.max_hp = 100
        self.hp = max(0, self.max_hp)
        self.armor = 0
        self.max_ammo = 6
        self.num_of_bullets = self.max_ammo
        self.dmg = 100
        self.attk_spd = 2
        self.reload_spd = 1
        self.crit_rate = 0.1
        self.crit_dmg = 0.5
        self.wallet = 0
        self.cursor = "img"

        self.shooting = True
        self.reloading = False

        self.next_allowed_shot_time = pygame.time.get_ticks() +  300
        self.reload_finish_time = 0

        self.mny_mod = 0
        self.cam_spd = 10


    def draw_UI(self):
        profile_rect = Container(x = SC_W//2 - 250, y= SC_H - (64+(PADDING*2)), width=500, height=250, color=WHITE)
        profile_rect.draw_rect()

        # Wallet container (bottom-left)
        wallet_x = profile_rect.rect.right - (64+PADDING)
        wallet_y = profile_rect.rect.top + PADDING
        wallet_container = Container(x=wallet_x, y=wallet_y, width=64, height=64, color=DESERT)
        wallet_container.draw_rect()

        # Gun chamber
        chamber_x = profile_rect.rect.centerx - 150
        chamber_y = SC_H - 150
        chamber_container = Container(x=chamber_x, y=chamber_y, width=300, height=300, color=WHITE)
        chamber_container.draw_rect()

        # Ammo container (top-left)
        ammo_x = profile_rect.rect.left + PADDING
        ammo_y = profile_rect.rect.top + PADDING
        ammo_container = Container(x=ammo_x, y=ammo_y, width=64, height=64, color=DESERT)
        ammo_container.draw_rect()

        # Fonts
        font = pygame.font.Font(FONT_PATH, 32)

        # --- Draw Wallet ---
        wallet = getattr(self, "wallet", 0)
        wallet_text = font.render(f"{wallet}$", True, BLACK)
        wallet_rect = wallet_text.get_rect(center=(wallet_x + wallet_container.width // 2, wallet_y + wallet_container.height // 2))
        SCREEN.blit(wallet_text, wallet_rect)

        # --- Draw Ammo ---
        ammo = getattr(self, "max_ammo", 0)
        bullets = getattr(self, "num_of_bullets", 0)
        ammo_text = font.render(f"{bullets}/{ammo}", True, BLACK)
        ammo_rect = ammo_text.get_rect(center=(ammo_x + ammo_container.width // 2, ammo_y + ammo_container.height // 2))
        SCREEN.blit(ammo_text, ammo_rect)

    def draw_Object(self, camera):
        self.pos = self.rect.move(camera.offset_x, camera.offset_y)
        self.rect.x, self.rect.y = self.pos.x, self.pos.y

        print(self.pos.x, self.rect.x, "pos")

        pygame.draw.rect(SCREEN, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)
        pygame.draw.rect(SCREEN, self.color, self.rect, border_radius=8)


        font = pygame.font.Font(FONT_PATH, 20)
        hp_txt = f"{self.hp}/{self.max_hp}"
        text_surface = font.render(hp_txt, True, BLACK)
        text_rect = text_surface.get_rect(
        center=(self.rect.centerx, self.rect.bottom + 20)
        )
        SCREEN.blit(text_surface, text_rect)

    def update(self, events, camera):
        now = pygame.time.get_ticks()
        # Finish reload
        if self.reloading and now >= self.reload_finish_time:
            self.num_of_bullets = self.max_ammo
            self.reloading = False
            print("Reload complete")

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.shoot(camera)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.start_reload()

        return None, 0
        
    def shoot(self, camera):
        now = pygame.time.get_ticks()
        mx, my = pygame.mouse.get_pos()
        hit_pos = pygame.Vector2(mx + camera.offset_x, my + camera.offset_y)

        if self.reloading:
            return None, 0

        if now < self.next_allowed_shot_time:
            return None, 0

        if self.num_of_bullets <= 0:
            self.start_reload()
            return None, 0

        self.num_of_bullets -= 1
        self.next_allowed_shot_time = now + int(1000 / self.attk_spd)
        print("Shot")

        is_crit = random.random() < self.crit_rate  # crit_rate = 0.0 to 1.0
        damage = self.dmg + (self.dmg * (self.crit_dmg if is_crit else 0))

        return hit_pos, damage

    def start_reload(self):
        if self.reloading:
            return

        print("Reloading...")
        self.reloading = True
        self.reload_finish_time = pygame.time.get_ticks() + int(1000 / self.reload_spd)

    def gain_reward(self, reward):
        self.wallet += (reward + self.mny_mod)

    def take_dmg(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.destroyed = True


class Enemy(Serializable):
    def __init__(self, x, y, w, h, e_type):
        # === Object ===
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, w, h)
        self.color = RED
        self.destroyed = False
        self.behaviour_type = e_type

        # === Stats ===
        self.max_hp = 100
        self.hp = self.max_hp
        self.dmg = 1
        self.attk_spd = 1
        self.crit_rate = 0.1
        self.crit_dmg = 0.1
        self.reward = 10

        # === Mov Stats ===
        self.mov_spd = 50
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.max_spd = self.mov_spd


        self.attack_timer = 0.0
        self.bullets = []
        self.visible = False  # enemy starts hidden


    def to_dict(self):
        data = super().to_dict()
        data["bullets"] = [b.to_dict() for b in self.bullets]
        data["enemy_type"] = self.behaviour_type
        return data
    
    @classmethod
    def from_dict(cls, data):
        rect_data = data["rect"]  # [x, y, w, h]
        e_type = data["enemy_type"]
        enemies = cls(*rect_data["value"], e_type)
        enemies.bullets = [
            Bullet.from_dict(b) for b in data["bullets"]
        ]
        return enemies

    def draw(self, camera):
        if self.destroyed:
            return
        
        offset_rect = self.rect.move(camera.offset_x, camera.offset_y)

        print(self.pos.x, self.rect.x, "enemypos")
        pygame.draw.rect(SCREEN, self.color, offset_rect)

        if self.hp < self.max_hp:
            # Health bar
            hp_ratio = max(0, self.hp / self.max_hp)
            bar_width = self.rect.width
            bar_height = 6
            bar_x = self.pos.x
            bar_y = self.pos.y + self.rect.height + 10

            pygame.draw.rect(SCREEN, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(SCREEN, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))

    def update(self, player, dt, camera):

        self.attack_timer += dt
        target_pos = pygame.Vector2(player.rect.center)
        pos = pygame.Vector2(self.rect.center)
        direction = target_pos - pos
        distance = direction.length()

        # Move in the direction of the package
        if distance > 1:
            direction.normalize_ip()
            self.acc = direction * self.max_spd
            self.enemy_mov(dt)

        # Attack pattern
        if self.behaviour_type == "melee":
            self.behaviour_melee(player, dt, direction, camera)
        elif self.behaviour_type == "range":
            self.behaviour_range(target_pos, distance, direction, dt, camera)
        elif self.behaviour_type == "bomber":
            self.behaviour_bomb(target_pos, distance, direction)
        # else:
        #     # Move in the direction of the package
        #     if distance > 1:
        #         direction.normalize_ip()
        #         self.acc = direction * self.max_spd

        # self.rect.x, self.rect.y = self.pos.x, self.pos.y


    # --- Behaviour patterns ---
    def behaviour_melee(self, target, dt, direction, camera):
        target_rect = target.rect
        # Check collision
        if self.resolve_collision(target_rect):
            # Stop moving
            self.vel *= 0
            self.acc *= 0

            # Attack
            attack_interval = 1 / self.attk_spd
            if self.attack_timer >= attack_interval:
                target.take_dmg(self.dmg)
                self.attack_timer = 0
            else:
                self.enemy_mov(dt, direction, camera)


    def behaviour_range(self, target, distance, direction, dt, camera):
        DESIRED_RADIUS = 250
        TOLERANCE = 10

        if distance > DESIRED_RADIUS + TOLERANCE:
            direction.normalize_ip()
            self.acc = direction * self.max_spd

        elif distance < DESIRED_RADIUS - TOLERANCE:
            direction.normalize_ip()
            self.acc = -direction * self.max_spd

        else:
            # Shoot
            attack_interval = 1 / self.attk_spd
            if self.attack_timer >= attack_interval:
                bullet = self.shoot(target)
                self.bullets.append(bullet)  # handled by Game
                self.attack_timer = 0

    def behaviour_bomb(self, target, distance, direction):
        DESIRED_RADIUS = 250
        TOLERANCE = 10

        if distance > DESIRED_RADIUS + TOLERANCE:
            direction.normalize_ip()
            self.acc = direction * self.max_spd

        elif distance < DESIRED_RADIUS - TOLERANCE:
            direction.normalize_ip()
            self.acc = -direction * self.max_spd

        else:
            # Shoot
            attack_interval = 1 / self.attk_spd
            if self.attack_timer >= attack_interval:
                bullet = self.shoot(target)
                self.bullets.append(bullet)  # handled by Game
                self.attack_timer = 0

    def enemy_mov(self, dt):
        self.vel += self.acc * dt

        # Clamp speed
        if self.vel.length() > self.max_spd:
            self.vel.scale_to_length(self.max_spd)

        # Move enemy
        self.pos.x += self.vel.x * dt 
        self.pos.y += self.vel.y * dt 


        # Reset acceleration every frame
        self.acc.update(0, 0)

    def resolve_collision(self, other_rect):
        if not self.rect.colliderect(other_rect):
            return False

        # Calculate overlap
        dx = self.rect.centerx - other_rect.centerx
        dy = self.rect.centery - other_rect.centery

        overlap_x = (self.rect.width / 2 + other_rect.width / 2) - abs(dx)
        overlap_y = (self.rect.height / 2 + other_rect.height / 2) - abs(dy)

        if overlap_x < overlap_y:
            # Push horizontally
            if dx > 0:
                self.rect.x += overlap_x
            else:
                self.rect.x -= overlap_x
            self.vel.x = 0
        else:
            # Push vertically
            if dy > 0:
                self.rect.y += overlap_y
            else:
                self.rect.y -= overlap_y
            self.vel.y = 0

        return True

    def shoot(self, target_pos):
        bullet = Bullet(
            x=self.rect.centerx,
            y=self.rect.centery,
            target=target_pos,
            dmg=self.dmg
        )
        return bullet

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.destroyed = True

    def apply_difficulty(self, mult):
        self.max_hp = int(self.max_hp * mult)
        self.hp =  max(0, self.max_hp)
        self.dmg *= mult
        self.attk_spd *= mult
        self.mov_spd *= mult
        self.max_spd = self.mov_spd
        self.crit_rate *= mult
        self.crit_dmg *= mult


class EnemySpawner(Serializable):
    def __init__(self, rectmap):
        self.rectmap = rectmap
        self.spawn_timer = 0.0
        self.spawn_interval = 1.0
        self.max_enemies = 10
        self.spawned_enemies = []

    def to_dict(self):
        data = super().to_dict()
        data["spawned_enemies"] = [e.to_dict() for e in self.spawned_enemies]
        return data

    def update(self, dt, multi):
        self.spawn_timer += dt
        enemies = self.spawned_enemies

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0

            if len(enemies) < self.max_enemies:
                self.spawn_enemy(multi)

        self.spawn_interval /= multi
        self.max_enemies =  int(self.max_enemies*multi)

    def spawn_enemy(self, multiplier):
        x = random.randint(self.rectmap.left + 10, self.rectmap.right - 10)
        y = random.randint(self.rectmap.top + 10, self.rectmap.bottom - 10)
        enemy_type = random.choice(["melee", "range"])

        enemy = Enemy(x, y, 50, 50, enemy_type)
        enemy.apply_difficulty(multiplier)

        self.spawned_enemies.append(enemy)

    @classmethod
    def from_dict(cls, data, rectmap):
        spawner = cls(rectmap)

        spawner.spawned_enemies = [
            Enemy.from_dict(e) for e in data["spawned_enemies"]
        ]
        return spawner


class Item(Serializable):
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, 50, 50)
        self.color = GREEN
        self.heal_percent = 0.05  # 5%

        self.destroyed = False

    def draw(self, camera):
        if self.destroyed:
            return
        
        posx, posy = self.pos.x + camera.offset_x, self.pos.y + camera.offset_y
        self.rect.center = (posx, posy)
        pygame.draw.rect(SCREEN, self.color, self.rect)

    def on_click(self, package):
        if self.destroyed:
            return

        # Heal 5% of max HP
        heal_amount = int(package.max_hp * self.heal_percent)
        package.hp = min(package.hp + heal_amount, package.max_hp)

        self.destroyed = True


class ItemSpawner(Serializable):
    def __init__(self):
        self.spawn_timer = 0.0
        self.spawn_interval = 2.0
        self.max_item = 5
        self.spawned_items = []

    def to_dict(self):
        data = super().to_dict()
        data["spawned_items"] = [i.to_dict() for i in self.spawned_items]
        return data

    def update(self, dt):
        self.spawn_timer += dt
        items = self.spawned_items

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0

            if len(items) < self.max_item:
                self.spawn_item()


    def spawn_item(self):
        x = random.randint(10, SC_W - 10)
        y = random.randint(10, SC_H - 10)
        item = Item(x, y)
        self.spawned_items.append(item)

    @classmethod
    def from_dict(cls, data):
        item_spawner = cls()
        item_spawner.spawned_items = [
            Item.from_dict(i) for i in data["spawned_items"]
        ]
        return item_spawner
        
class Upgrade():
    def __init__(self):
        # === Object ===
        self.color = DESERT
        # === Upgrade Items ===
        self.upgrade_items = [
            {"stat": "max_hp", "label": "Max HP", "cost": 10, "mod": 10},
            {"stat": "armor", "label": "Armor", "cost": 10, "mod": 1},
            {"stat": "dmg", "label": "Damage", "cost": 10, "mod": 10},
            {"stat": "max_ammo", "label": "Max Ammo", "cost": 10, "mod": 1},
            {"stat": "attk_spd", "label": "Attack Speed", "cost": 10, "mod": 0.5},
            {"stat": "reload_spd", "label": "Reload Speed", "cost": 10, "mod": 0.5},
            {"stat": "crit_rate", "label": "Crit Rate", "cost": 10, "mod": 0.01},
            {"stat": "crit_dmg", "label": "Crit Damage", "cost": 10, "mod": 0.1},
            {"stat": "mny_mod", "label": "Money Gain", "cost": 10, "mod": 10},
        ]

        self.cards = []
        self.click_locked = True
        self.show_menu = False
        self.scroll_offset = 0
        self.scroll_speed = 30


    # Create buttons once
    def upgrade_menu(self, player):   
        m_pos = pygame.mouse.get_pos()  
        self.cards.clear()  # 🔥 CRITICAL    
        up_container = Container(x = 200, y=200,  width=750, height=500, color= WHITE)
        up_container.draw_rect()

        cards_section_w = up_container.rect.width - (MARGIN * 2)
        cards_section_h = up_container.rect.height - (MARGIN * 2)
        card_sect_rect = pygame.Rect(
            up_container.rect.x + MARGIN,
            up_container.rect.y + MARGIN,
            cards_section_w,
            cards_section_h
        )

        card_w = 200
        card_h = 200
        gap = MARGIN

        cols = max(1, cards_section_w // (card_w + gap))

        total_grid_width = cols * card_w + (cols - 1) * gap
        start_x = up_container.rect.centerx - total_grid_width // 2
        start_y = up_container.rect.y + MARGIN - self.scroll_offset
 
        total_rows = (len(self.upgrade_items) + cols - 1) // cols
        total_content_height = total_rows * card_h + (total_rows - 1) * gap
        max_scroll = max(0, total_content_height - cards_section_h)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        for i, upgrade in enumerate(self.upgrade_items):
            row = i // cols
            col = i % cols

            x = start_x + col * (card_w + gap)
            y = start_y + row * (card_h + gap)

            rect = pygame.Rect(x, y, card_w, card_h)

            self.cards.append({
                "rect": rect,
                "data": upgrade
            })

        SCREEN.set_clip(card_sect_rect)
        # --- draw cards + data ---
        for i, card in enumerate(self.cards):
            upgrade = card["data"]

            hover = card["rect"].collidepoint(m_pos)
            color = LIGHT_GRAY if hover else self.color
            pygame.draw.rect(SCREEN, color, card["rect"], border_radius=12)

            # image placeholder
            image_rect = pygame.Rect(
                card['rect'].centerx - 35,
                card['rect'].y + PADDING * 2,
                64,
                64
            )
            pygame.draw.rect(SCREEN, WHITE, image_rect, border_radius=8)
            pygame.draw.rect(SCREEN, WHITE, image_rect, 2, border_radius=8)

            font = pygame.font.Font(FONT_PATH, 20)

            # Get current value from package first, then player
            stat = upgrade['stat']
            if hasattr(player, stat):
                current = getattr(player, stat)
            else:
                current = 0

            # --- TEXT ---
            label_surf = font.render(f"{upgrade['label']}: {current} (+{upgrade['mod']})", True, BLACK)
            cost_surf = font.render(f"Cost: ${upgrade['cost']}", True, BLACK)

            SCREEN.blit(label_surf, (card['rect'].x + PADDING, image_rect.bottom + PADDING))
            SCREEN.blit(cost_surf, (card['rect'].x + PADDING, image_rect.bottom + PADDING + 25))


        SCREEN.set_clip(None)


        return self.click(m_pos, player)


    def click(self, m_pos, player):
        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0] and not self.click_locked:
            for card in self.cards:
                if card["rect"].collidepoint(m_pos):
                    self.add_upgrade(player, card['data'])
                    self.click_locked = True  # lock until release

        elif not mouse_buttons[0]:
            self.click_locked = False  # unlock when button released

    def add_upgrade(self, player, upgrade_data):
        stat = upgrade_data["stat"]
        effect_value = upgrade_data["mod"]
        cost_value = upgrade_data["cost"]

        if player.wallet < cost_value:
            print("Not enough money")
            return

        if hasattr(player, stat):
            target = player
        else:
            print(f"Stat '{stat}' not found")
            return

        current = getattr(target, stat)
        new_value = round(current + effect_value, 2)
        setattr(target, stat, new_value)

        print(f"{stat} upgraded to {new_value}")

        # Deduct money
        player.wallet -= cost_value

        # Increase cost for next upgrade (scaling)
        upgrade_data["cost"] += 10

    # def add_upgrade(self, player, package, stat):
    #     info = self.upgrade_items[stat]
    #     cost = info["cost"]

    #     # Check money
    #     if player.wallet < cost:
    #         print("Not enough money")
    #         return

    #     # Determine target (package or player)
    #     if hasattr(package, stat):
    #         target = package
    #     elif hasattr(player, stat):
    #         target = player
    #     else:
    #         print(f"Stat '{stat}' not found")
    #         return

    #     # Apply upgrade
    #     current = getattr(target, stat)
    #     new_value = round(current + info["mod"], 2)
    #     setattr(target, stat, new_value)

    #     # Deduct money
    #     player.wallet -= cost

    #     # Increase cost for next upgrade (scaling)
    #     info["cost"] += 10

    #     print(f"{stat} upgraded to {new_value}, next cost: {info['cost']}")

            


        # spacing = 60
        # start_y = container.posy + 10
        # for i, stat in enumerate(self.upgrade_items):
        #     btn_y = start_y + i * spacing
        #     bttn = Button(
        #         x=container.posx + 10,
        #         y=btn_y,
        #         width=280,
        #         height=50,
        #         color=DESERT,
        #         text="",              # ← text set dynamically
        #         text_color=BLACK,
        #         font_size=25,
        #         action=stat           # ← stat name like "max_hp"
        #     )
        #     self.buttons.append(bttn)


    # # Draw buttons and handle hover
    # def draw(self, player, package):
    #     for btn in self.buttons:
    #         stat = btn.action
    #         info = self.upgrade_items[stat]

    #         # Get current value from package first, then player
    #         if hasattr(package, stat):
    #             current = getattr(package, stat)
    #         elif hasattr(player, stat):
    #             current = getattr(player, stat)
    #         else:
    #             current = 0

    #         # Update button text
    #         btn.text = f"{info['label']}: {current}  (+{info['mod']})  ${info['cost']}"

    #         hover = btn.rect.collidepoint(pygame.mouse.get_pos())
    #         btn.draw(hover=hover)