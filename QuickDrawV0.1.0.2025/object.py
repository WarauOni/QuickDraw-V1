import pygame
from config import *
import random

class DifficultyManager(Serializable):
    def __init__(self):
        self.elapsed_time = 0.0
        self.level = 0
        self.interval = 300.0  # 5 minutes
        self.scale = 1.1       # 10%

    def draw(self, screen, game_container_rect):
        # Positioning
        x, y = (game_container_rect.w // 2) - 100, game_container_rect.y + 10
        width, height = 200, 50

        # Draw background container
        time_container = Container(x=x, y=y, width=width, height=height, color=DESERT)
        time_container.draw_rect(screen)


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
        screen.blit(text_surface, text_rect)

        # Optional: show difficulty level
        level_surface = font.render(f"Level {self.level}", True, BLACK)
        level_rect = level_surface.get_rect(midtop=(x + width // 2, y + height + 5))
        screen.blit(level_surface, level_rect)


    def update(self, dt):
        self.elapsed_time += dt
        if self.elapsed_time >= self.interval:
            self.elapsed_time -= self.interval
            self.level += 1

    def multiplier(self):
        return self.scale ** self.level

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

    def draw(self, screen, hover=False):
        color = (255, 50, 50) if hover else self.color
        # Draw border (slightly bigger rectangle)
        pygame.draw.rect(screen, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)

        # Draw actual button
        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        # Load font (custom or default)
        font = pygame.font.Font(self.font_path, self.font_size) if self.font_path else pygame.font.Font(None, self.font_size)
        
        # Render text
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

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

    def draw_rect(self, screen, hover=False):
        color = (255, 50, 50) if hover else self.color
        pygame.draw.rect(screen, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)

    def draw_circle(self, screen, camera_offset, center_x, center_y):
        pygame.draw.circle(screen, (255, 255, 255), (int(center_x), int(center_y)), WORLD_RADIUS)
        pygame.draw.circle(screen, (255, 0, 0), (int(center_x), int(center_y)), WORLD_RADIUS, 5)

    def draw_opaque(self, screen, snapshot):
        screen.blit(snapshot, (0, 0))
        # Create transparent overlay surface
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        # Fill with color (RGBA) — make sure self.color has 4 values
        overlay.fill(self.color)

        # Draw border if needed
        pygame.draw.rect(screen, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)

        # Blit overlay with transparency
        screen.blit(overlay, (self.posx, self.posy))

class Bullet(Serializable):
    def __init__(self, x, y, target, dmg):
        self.pos = pygame.Vector2(x, y)
        self.dmg = dmg
        self.speed = 400
        self.radius = 4

        direction = pygame.Vector2(target) - self.pos
        self.vel = direction.normalize() * self.speed

    def update(self, dt):
        self.pos += self.vel * dt

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 50, 50), self.pos, self.radius)



class Player(Serializable):
    def __init__(self):
        self.max_ammo = 6
        self.num_of_bullets = self.max_ammo
        self.dmg = 10
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

        self.mny_bnty = 10

    def draw(self, screen, game_container_rect):
        # Positioning and sizes
        padding = 10
        container_w, container_h = 200, 50

        # Wallet container (bottom-left)
        wallet_x = game_container_rect.x + padding
        wallet_y = game_container_rect.y + padding
        wallet_container = Container(x=wallet_x, y=wallet_y, width=container_w, height=container_h, color=DESERT)
        wallet_container.draw_rect(screen)

        # Ammo container (top-left)
        ammo_x = game_container_rect.x + padding
        ammo_y = game_container_rect.h - container_h - padding 
        ammo_container = Container(x=ammo_x, y=ammo_y, width=container_w, height=container_h, color=DESERT)
        ammo_container.draw_rect(screen)

        # Fonts
        font = pygame.font.Font(FONT_PATH, 32)

        # --- Draw Wallet ---
        wallet = getattr(self, "wallet", 0)
        wallet_text = font.render(f"{wallet}$", True, BLACK)
        wallet_rect = wallet_text.get_rect(center=(wallet_x + container_w // 2, wallet_y + container_h // 2))
        screen.blit(wallet_text, wallet_rect)

        # --- Draw Ammo ---
        ammo = getattr(self, "max_ammo", 0)
        bullets = getattr(self, "num_of_bullets", 0)
        ammo_text = font.render(f"{bullets}/{ammo}", True, BLACK)
        ammo_rect = ammo_text.get_rect(center=(ammo_x + container_w // 2, ammo_y + container_h // 2))
        screen.blit(ammo_text, ammo_rect)


    def update(self, events):
        now = pygame.time.get_ticks()

        # Finish reload
        if self.reloading and now >= self.reload_finish_time:
            self.num_of_bullets = self.max_ammo
            self.reloading = False
            print("Reload complete")

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.shoot()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.start_reload()


        return None, 0
        
    def shoot(self):
        now = pygame.time.get_ticks()

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

        return pygame.mouse.get_pos(), damage

    def start_reload(self):
        if self.reloading:
            return

        print("Reloading...")
        self.reloading = True
        self.reload_finish_time = pygame.time.get_ticks() + int(1000 / self.reload_spd)


class Enemy(Serializable):
    def __init__(self, x, y, e_type):
        self.max_hp = 100
        self.hp = max(0, self.max_hp)
        self.dmg = 1
        self.attk_spd = 1
        self.crit_rate = 1
        self.crit_dmg = 1
        self.spd = 50
        self.vel = pygame.Vector2(0, 0)
        self.acc = pygame.Vector2(0, 0)
        self.max_spd = self.spd
        self.attack_timer = 0.0
        self.rect = pygame.Rect(x, y, 50, 50)
        self.color = RED
        self.destroyed = False
        self.behaviour_type = e_type
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
        enemies = cls(rect_data[0], rect_data[1], e_type)

        enemies.bullets = [
            Bullet.from_dict(b) for b in data["bullets"]
        ]
        return enemies

    def draw(self, screen):
        if self.destroyed:
            return

        
        if self.visible:
            pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))

            if self.hp < self.max_hp:
                # Health bar
                hp_ratio = max(0, self.hp / self.max_hp)
                bar_width = self.rect.width
                bar_height = 6
                bar_x = self.rect.x
                bar_y = self.rect.y + self.rect.height + 10

                pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))

    def update(self, package, dt, game_container_rect):
        self.attack_timer += dt

        target_pos = pygame.Vector2(package.rect.center)
        pos = pygame.Vector2(self.rect.center)
        direction = target_pos - pos
        distance = direction.length()

        # If not yet visible, move towards the package
        if not self.visible:
            # Move in the direction of the package
            if distance > 1:
                direction.normalize_ip()
                self.acc = direction * self.max_spd

            # Check if enemy has entered the game container
            if game_container_rect.contains(self.rect):
                self.visible = True  # now it appears fully
    

        """Run AI depending on enemy type."""
        if self.behaviour_type == "melee":
            self.behaviour_melee(package, dt)
        elif self.behaviour_type == "range":
            self.behaviour_range(package, dt)
        else:
            self.behaviour_idle()

        self.enemy_mov(dt)

    # --- Behaviour patterns ---
    def behaviour_melee(self, package, dt):
        target_rect = package.rect

        # Move towards package
        target = pygame.Vector2(target_rect.center)
        pos = pygame.Vector2(self.rect.center)
        direction = target - pos
        distance = direction.length()

        # Check collision
        if self.rect.colliderect(target_rect):
            # Stop moving
            self.vel *= 0
            self.acc *= 0

            # Attack
            attack_interval = 1 / self.attk_spd
            if self.attack_timer >= attack_interval:
                package.hp -= self.dmg
                self.attack_timer = 0
        else:
            # Move closer
            if distance > 1:
                direction.normalize_ip()
                self.acc = direction * self.max_spd

        self.enemy_mov(dt)

    def behaviour_range(self, package, dt):
        target = pygame.Vector2(package.rect.center)
        pos = pygame.Vector2(self.rect.center)
        direction = target - pos
        distance = direction.length()

        DESIRED_RADIUS = 250
        TOLERANCE = 10

        if distance > DESIRED_RADIUS + TOLERANCE:
            direction.normalize_ip()
            self.acc = direction * self.max_spd

        elif distance < DESIRED_RADIUS - TOLERANCE:
            direction.normalize_ip()
            self.acc = -direction * self.max_spd

        else:
            # Stop movement
            self.vel *= 0
            self.acc *= 0

            # Shoot
            attack_interval = 1 / self.attk_spd
            if self.attack_timer >= attack_interval:
                bullet = self.shoot(package.rect.center)
                self.bullets.append(bullet)  # handled by Game
                self.attack_timer = 0

        self.enemy_mov(dt)

    def behaviour_idle(self):
        pass


    def enemy_mov(self, dt):
        # Apply acceleration to velocity
        self.vel += self.acc * dt

        # Clamp speed
        if self.vel.length() > self.max_spd:
            self.vel.scale_to_length(self.max_spd)

        # Move enemy
        self.rect.x += self.vel.x * dt
        self.rect.y += self.vel.y * dt

        # Reset acceleration every frame
        self.acc.update(0, 0)

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
        self.spd *= mult
        self.max_spd = self.spd
        self.crit_rate *= mult
        self.crit_dmg *= mult


class EnemySpawner(Serializable):
    def __init__(self, game_container_rect):
        self.game_container_rect = game_container_rect
        self.spawn_timer = 0.0
        self.spawn_interval = 5.0
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
        x, y = get_random_spawn_pos(self.game_container_rect)
        enemy_type = random.choice(["melee", "range"])

        enemy = Enemy(x, y, enemy_type)
        enemy.apply_difficulty(multiplier)

        self.spawned_enemies.append(enemy)

    @classmethod
    def from_dict(cls, data, game_container_rect):
        spawner = cls(game_container_rect)

        spawner.spawned_enemies = [
            Enemy.from_dict(e) for e in data["spawned_enemies"]
        ]
        return spawner


class Item(Serializable):
    def __init__(self, x, y):
        self.destroyed = False
        self.rect = pygame.Rect(x, y, 50, 50)
        self.color = GREEN
        self.heal_percent = 0.05  # 5%

    def draw(self):
        if self.destroyed:
            return
        
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))

    def on_click(self, package):
        if self.destroyed:
            return

        # Heal 5% of max HP
        heal_amount = int(package.max_hp * self.heal_percent)
        package.hp = min(package.hp + heal_amount, package.max_hp)

        self.destroyed = True


class ItemSpawner(Serializable):
    def __init__(self, game_container_rect):
        self.game_container_rect = game_container_rect
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
        x = random.randint(self.game_container_rect.left + 10, self.game_container_rect.right - 50)
        y = random.randint(self.game_container_rect.top + 10, self.game_container_rect.bottom -50)

        item = Item(x, y)

        self.spawned_items.append(item)

    @classmethod
    def from_dict(cls, data, game_container_rect):
        item_spawner = cls(game_container_rect)

        item_spawner.spawned_items = [
            Item.from_dict(i) for i in data["spawned_items"]
        ]
        return item_spawner
        
        
class Package():
    def __init__(self, x, y, width, height, color, border_color, border_size):
        self.max_hp = 100
        self.hp = max(0, self.max_hp)
        self.armor = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.border_color = border_color
        self.border_size = border_size

    def draw(self, screen):
        pygame.draw.rect(screen, self.border_color, self.rect.inflate(self.border_size * 2, self.border_size * 2), border_radius=8)
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)

        if self.hp < self.max_hp:

            # Health bar
            hp_ratio = max(0, self.hp / self.max_hp)
            bar_width = self.rect.width
            bar_height = 6
            bar_x = self.rect.x
            bar_y = self.rect.y + self.rect.height + 10

            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, bar_height))


class Upgrade():
    def __init__(self):
        # Upgrade items
        self.upgrade_items = {
            "max_hp":    {"label": "Max HP",        "cost": 10, "mod": 10},
            "armor":     {"label": "Armor",         "cost": 10, "mod": 1},
            "dmg":       {"label": "Damage",        "cost": 10, "mod": 10},
            "max_ammo":  {"label": "Max Ammo",      "cost": 10, "mod": 1},
            "attk_spd":  {"label": "Attack Speed",  "cost": 10, "mod": 0.5},
            "reload_spd":{"label": "Reload Speed",  "cost": 10, "mod": 0.5},
            "crit_rate": {"label": "Crit Rate",     "cost": 10, "mod": 0.01},
            "crit_dmg":  {"label": "Crit Damage",   "cost": 10, "mod": 0.1},
            "mny_bnty":  {"label": "Money Gain",    "cost": 10, "mod": 10},
        }


        self.buttons = []
        self.click_locked = True

    # Create buttons once
    def create_buttons(self, container):
        spacing = 60
        start_y = container.posy + 10

        for i, stat in enumerate(self.upgrade_items):
            btn_y = start_y + i * spacing
            bttn = Button(
                x=container.posx + 10,
                y=btn_y,
                width=280,
                height=50,
                color=DESERT,
                text="",              # ← text set dynamically
                text_color=BLACK,
                font_size=25,
                action=stat           # ← stat name like "max_hp"
            )
            self.buttons.append(bttn)

    # Draw buttons and handle hover
    def draw(self, player, package):
        for btn in self.buttons:
            stat = btn.action
            info = self.upgrade_items[stat]

            # Get current value from package first, then player
            if hasattr(package, stat):
                current = getattr(package, stat)
            elif hasattr(player, stat):
                current = getattr(player, stat)
            else:
                current = 0

            # Update button text
            btn.text = f"{info['label']}: {current}  (+{info['mod']})  ${info['cost']}"

            hover = btn.rect.collidepoint(pygame.mouse.get_pos())
            btn.draw(screen, hover=hover)

    def click(self, player, package):
        m_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        if mouse_buttons[0] and not self.click_locked:
            for btn in self.buttons:
                if btn.rect.collidepoint(m_pos):
                    self.add_upgrade(player, package, btn.action)
                    self.click_locked = True  # lock until release

        elif not mouse_buttons[0]:
            self.click_locked = False  # unlock when button released


    def add_upgrade(self, player, package, stat):
        info = self.upgrade_items[stat]
        cost = info["cost"]

        # Check money
        if player.wallet < cost:
            print("Not enough money")
            return

        # Determine target (package or player)
        if hasattr(package, stat):
            target = package
        elif hasattr(player, stat):
            target = player
        else:
            print(f"Stat '{stat}' not found")
            return

        # Apply upgrade
        current = getattr(target, stat)
        new_value = round(current + info["mod"], 2)
        setattr(target, stat, new_value)

        # Deduct money
        player.wallet -= cost

        # Increase cost for next upgrade (scaling)
        info["cost"] += 10

        print(f"{stat} upgraded to {new_value}, next cost: {info['cost']}")

            


