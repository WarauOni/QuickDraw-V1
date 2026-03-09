import pygame
from config import *
import json
from entity import *

# Initialize pygame
pygame.init()


class Game():
    def __init__(self, load_data = None):
        self.screen_center = [SC_W//2, SC_H//2]
        self.rectmap = RectMap(x=self.screen_center[0]-WORLD_SIZE//2, y=self.screen_center[1]-WORLD_SIZE//2, width=WORLD_SIZE, height=WORLD_SIZE, color=WHITE)
        self.game_over = False

        if load_data:
            self.player = Player.from_dict(load_data["player"])
            self.spawner = EnemySpawner.from_dict(load_data["spawners"], self.rectmap.rect)
            self.items_spawn = ItemSpawner.from_dict(load_data["items"])
            # assign enemies etc.
        else:
            self.player = Player(x = self.rectmap.rect.centerx - 75, y = self.rectmap.rect.centery - 37.5, width=125, height=75, color=RED, border_color=BLACK, border_size=2)
            self.spawner = EnemySpawner(self.rectmap.rect)
            self.items_spawn = ItemSpawner()
            
        # self.carriage = Carriage(x = self.screen_center[0] - 75, y = self.screen_center[1] - 37.5, width=125, height=75, color=RED, border_color=BLACK, border_size=2)
        self.upgrade = Upgrade()
        self.difficulty = DifficultyManager()
        self.camera = Camera(SC_W, SC_H)

    def game_over_screen(self, snapshot):
        bttn_items = ['try again', 'main menu']
        bttns = []
        go_screen = Container(
            x=(SC_W // 2)-300,
            y=(SC_H // 2)-100,
            width=600,
            height=200,
            color= WHITE
        )
        spacing = 250
        button_width = 200
        button_height = 50
        gap = 40
        total_width = 2 * button_width + gap
        start_x = go_screen.posx + (go_screen.rect.width - total_width) // 2
        button_y = go_screen.posy + 120

        # Create buttons only once
        for i, label in enumerate(bttn_items):
            btn_x = start_x + i * spacing
            bttn = Button(
                x=btn_x,
                y=button_y,
                width=button_width,
                height=button_height,
                color=DESERT,
                text=label.upper(),
                text_color=BLACK,
                font_size=28,
                action=label  # Save action for identification
            )
            bttns.append(bttn)

        while True:
            SCREEN.blit(snapshot, (0, 0))
            go_screen.draw_rect(SCREEN)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for bttn in bttns:
                        if bttn.rect.collidepoint(event.pos):
                            return bttn.action

            # Draw buttons
            for bttn in bttns:
                hover = bttn.rect.collidepoint(pygame.mouse.get_pos())
                bttn.draw(hover=hover)

            # Draw title
            font = pygame.font.Font(None, 74)
            text = font.render("GAME OVER", True, (0, 0, 0))
            text_rect = text.get_rect(center=(go_screen.posx + go_screen.rect.width // 2, go_screen.posy+ 50))
            SCREEN.blit(text, text_rect)

            pygame.display.update()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            snapshot = SCREEN.copy()
            SCREEN.fill(DESERT)
            self.rectmap.draw(self.camera)
            self.rectmap.draw_border_overlay()
            dt = clock.tick(60) / 1000  # ← THIS LINE
            events = pygame.event.get()
            enemies = []
            self.difficulty.draw()
            self.difficulty.update(dt, self.spawner.spawned_enemies)
            self.camera.camera_control(self.player, self.rectmap)
            
            # Handle input/events
            for event in events:
                if event.type == pygame.QUIT:
                    save_game_data(self.player, self.spawner, self.items_spawn)
                    return "menu"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_b:
                        self.upgrade.show_menu = not self.upgrade.show_menu
                    elif event.key == pygame.K_ESCAPE:
                        player_data, spawner_data, items_data = save_game_data(self.player, self.spawner, self.items_spawn)
                        return {"state":"pause", "snapshot":snapshot, "saved_data": (player_data, spawner_data, items_data)}
                if event.type == pygame.MOUSEWHEEL:
                    self.upgrade.scroll_offset -= event.y * self.upgrade.scroll_speed
            

            # self.carriage.draw(self.camera)
            self.player.draw_UI()
            self.player.draw_Object(self.rectmap)
            hit_pos, dmg = self.player.update(events)  # or player.update()

            self.items_spawn.update(dt)
            for item in self.items_spawn.spawned_items:
                item.draw(self.camera)
                if hit_pos:
                    if not item.destroyed and item.rect.collidepoint(hit_pos):
                        item.on_click(self.player)

                if item.destroyed:
                    self.items_spawn.spawned_items.remove(item)

            mult = self.difficulty.multiplier()
            active = self.difficulty.state
            self.spawner.update(dt, mult, active)
            enemies.extend(self.spawner.spawned_enemies)
            for enemy in enemies:
                enemy.draw(self.camera)
                enemy.update(self.player, dt, self.camera)


                for other in self.spawner.spawned_enemies:
                    if other is not enemy and not other.destroyed:
                        enemy.resolve_collision(other.rect)

                # Prevent overlap with items
                for item in self.items_spawn.spawned_items:
                    if not item.destroyed:
                        enemy.resolve_collision(item.rect)

                for bullet in enemy.bullets[:]:
                    bullet.draw(self.camera)
                    bullet.update(dt)
                    if self.player.rect.colliderect(bullet.rect):
                        self.player.take_dmg(bullet.dmg)
                        enemy.bullets.remove(bullet)

                for bomb in enemy.bombs[:]:
                    bomb.draw(self.camera)
                    bomb.update(dt, self.player)
                    if hit_pos:
                        if not bomb.destroyed and bomb.rect.collidepoint(hit_pos):
                            bomb.on_click()
                    if bomb.destroyed:
                        enemy.bombs.remove(bomb)

                if hit_pos:
                    if not enemy.destroyed and enemy.rect.collidepoint(hit_pos):
                        enemy.take_damage(dmg)
                    
                        
                if enemy.destroyed:
                    self.spawner.spawned_enemies.remove(enemy)
                    self.player.gain_reward(enemy.reward)


            if self.player.hp <= 0 and not self.game_over:
                result = self.game_over_screen(snapshot)
                if result == "try again":
                    return "new_game"
                elif result == "main menu":
                    return "menu"
            
            if self.upgrade.show_menu:
                self.upgrade.upgrade_menu(self.player)


         

            snapshot = SCREEN.copy()
            pygame.display.flip()


def menu(events):
    menu_items = ["New Game","Load Game", "Settings", "Credits", "Quit"]
    container = Container(x=(SC_W//2) + 100, y=(SC_H//2)-300, width=500, height=600, color=(255, 255, 255))
    container.draw_rect()

    buttons = []
    spacing = 110
    start_y = container.posy + 30

    for i, label in enumerate(menu_items):
        btn_y = start_y + i * spacing
        bttn = Button(
            x=container.posx+50,
            y=btn_y,
            width=400,
            height=80,
            color=DESERT,
            text=label,
            text_color=BLACK,
            action=label.lower().replace(" ", "_")
        )
        hover = bttn.rect.collidepoint(pygame.mouse.get_pos())
        bttn.draw(hover=hover)
        buttons.append(bttn)

    # Handle clicks
    for event in events:
        if event.type == pygame.QUIT:
            return "quit"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                if btn.rect.collidepoint(event.pos):
                    return btn.action # e.g., "new_game"

    return "menu" # No change

def new_game():
    game = Game()
    return game.run()


def load_game():
    save_data = load_save_data()
    if save_data:
        game = Game(load_data=save_data)
        return game.run()
    else:
        print("⚠️ No save data")
        return "menu"

def setting():
    pass

def credit():
    pass

def pause_game(snapshot):
    bttn_items = ['play', 'main menu']
    bttns = []
    pause = True
    pause_screen = Container(
        x=(SC_W // 2)-300,
        y=(SC_H // 2)-100,
        width=600,
        height=200,
        color= WHITE
    )
    spacing = 250
    button_width = 200
    button_height = 50
    gap = 40
    total_width = 2 * button_width + gap
    start_x = pause_screen.posx + (pause_screen.rect.width - total_width) // 2
    button_y = pause_screen.posy + 120

    # Create buttons only once
    for i, label in enumerate(bttn_items):
        btn_x = start_x + i * spacing
        bttn = Button(
            x=btn_x,
            y=button_y,
            width=button_width,
            height=button_height,
            color=DESERT,
            text=label.upper(),
            text_color=BLACK,
            font_size=28,
            action=label  # Save action for identification
        )
        bttns.append(bttn)

    while pause:
        SCREEN.blit(snapshot, (0, 0))
        pause_screen.draw_rect()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                 return "resume"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for bttn in bttns:
                    if bttn.rect.collidepoint(event.pos):
                        if bttn.action == "play":
                            return "resume"
                        elif bttn.action == "main menu":
                            return "menu"

        # Draw buttons
        for bttn in bttns:
            hover = bttn.rect.collidepoint(pygame.mouse.get_pos())
            bttn.draw(hover=hover)

        # Draw title
        font = pygame.font.Font(None, 74)
        text = font.render("Pause", True, (0, 0, 0))
        text_rect = text.get_rect(center=(pause_screen.posx + pause_screen.rect.width // 2, pause_screen.posy+ 50))
        SCREEN.blit(text, text_rect)

        pygame.display.update()

def game_loop():
    running = True
    clock = pygame.time.Clock()
    state = "menu"
    while running:
        clock.tick(60)  # Limit frame rate to 60 FPS
        SCREEN.fill(DESERT)
        events = pygame.event.get()
            
        if state == 'menu':
            state = menu(events)
            pygame.display.flip()
            continue
        elif state == "new_game":
            result = new_game()
            if isinstance(result, dict):
                state = result["state"]
                snapshot = result.get("snapshot", None)  # save for pause menu
                player, spawners, items = result.get("saved_data", (None, []))
            else:
                state = result
            pygame.display.flip()
            continue
        elif state == "load_game":
            save_data = load_save_data()
            if save_data:
                result = load_game()
                state = result["state"]
                snapshot = result.get("snapshot", None)
            else:
                print("No valid save data. Returning to menu.")
                state = "menu"
        elif state == "setting":
            state = setting()
        elif state == "credit":
            state = credit()
        elif state == 'quit':
            running = False
        elif state == "pause":
            result = pause_game(snapshot)
            if result == "resume":
                snapshot = SCREEN.copy()
                state = "load_game"
            else:
                state = result

            
        pygame.display.flip()

    pygame.quit()


# Run the game
game_loop()
