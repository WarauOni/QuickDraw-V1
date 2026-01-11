import pygame
from config import *
import json
from object import *

# Initialize pygame
pygame.init()


class Game():
    def __init__(self, load_data = None):

        self.game_container = Container(x = 25, y=20, width=SCREEN_WIDTH-375, height=SCREEN_HEIGHT-40, color=(255, 255, 255))
        self.gm_containerx, self.gm_containery = 25 + self.game_container.width, 20 + self.game_container.height
        self.randx = random.randint(
            25,
            25 + self.game_container.width - 50
        )

        self.randy = random.randint(
            20,
            20 + self.game_container.height - 50
        )
        self.upgrade_container = Container(x = SCREEN_WIDTH-325, y=SCREEN_HEIGHT-(SCREEN_HEIGHT-130), width=300, height=SCREEN_HEIGHT-150, color=(255, 255, 255))


        if load_data:
            self.player = Player.from_dict(load_data["player"])
            self.spawner = EnemySpawner.from_dict(load_data["spawners"], self.game_container.rect)
            self.items_spawn = ItemSpawner.from_dict(load_data["items"], self.game_container.rect)
            # assign enemies etc.
        else:
            self.player = Player()
            self.spawner = EnemySpawner(self.game_container.rect)
            self.items_spawn = ItemSpawner(self.game_container.rect)
            
        self.pack = Package(x = (self.gm_containerx//2)-75, y = (self.gm_containery//2)-37.5, width=125, height=75, color=RED, border_color=BLACK, border_size=2)
        self.upgrade = Upgrade()
        self.upgrade.create_buttons(self.upgrade_container)
        self.difficulty = DifficultyManager()


    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            snapshot = screen.copy()
            dt = clock.tick(60) / 1000  # ← THIS LINE
            self.game_container.draw_rect(screen)
            self.upgrade_container.draw_rect(screen)
            self.upgrade.draw(self.player, self.pack)
            events = pygame.event.get()
            enemies = []
            self.difficulty.update(dt)
            self.difficulty.draw(screen, self.game_container.rect)
            
            # Handle input/events
            for event in events:
                if event.type == pygame.QUIT:
                    save_game_data(self.player, self.spawner, self.items_spawn)
                    return "menu"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    player_data, spawner_data, items_data = save_game_data(self.player, self.spawner, self.items_spawn)
                    return {"state":"pause", "snapshot":snapshot, "saved_data": (player_data, spawner_data, items_data)}
                

            self.pack.draw(screen)
            self.player.draw(screen, self.game_container.rect)
            hit_pos, dmg = self.player.update(events)  # or player.update()

            self.items_spawn.update(dt)
            for item in self.items_spawn.spawned_items:
                item.draw()
                if hit_pos:
                    if not item.destroyed and item.rect.collidepoint(hit_pos):
                        item.on_click(self.pack)

                if item.destroyed:
                    self.items_spawn.spawned_items.remove(item)

            multi = self.difficulty.multiplier()
            self.spawner.update(dt, multi)
            enemies.extend(self.spawner.spawned_enemies)
            for enemy in enemies:
                print("type",type(enemy), enemy)
                enemy.draw(screen)
                enemy.update(self.pack, dt, self.game_container.rect)

                for bullet in enemy.bullets[:]:
                    bullet.draw(screen)
                    bullet.update(dt)
                    if bullet.pos.distance_to(self.pack.rect.center) < bullet.radius + 20:
                        self.pack.hp -= bullet.dmg
                        enemy.bullets.remove(bullet)

                if hit_pos:
                    if not enemy.destroyed and enemy.rect.collidepoint(hit_pos):
                        enemy.take_damage(dmg)
                    
                        

                if enemy.destroyed:
                    self.spawner.spawned_enemies.remove(enemy)
                    self.player.wallet += self.player.mny_bnty


            if self.pack.hp <= 0:
                print("Package destroyed")
                return "menu"
            
            self.upgrade.click(self.player, self.pack)

            pygame.display.flip()

# Load JSON Records
def load_records():
    try:
        with open("records.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Return empty list if file not found


def menu(events):
    menu_items = ["New Game","Load Game", "Settings", "Credits", "Quit"]
    container = Container(x=(SCREEN_WIDTH//2) + 100, y=(SCREEN_HEIGHT//2)-300, width=500, height=600, color=(255, 255, 255))
    container.draw_rect(screen)

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
        bttn.draw(screen, hover=hover)
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

def pause_game(screen, snapshot):
    bttn_items = ['play', 'main menu']
    bttns = []
    pause = True
    pause_screen = Container(
        x=(SCREEN_WIDTH // 2)-300,
        y=(SCREEN_HEIGHT // 2)-100,
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
        screen.blit(snapshot, (0, 0))
        pause_screen.draw_rect(screen)

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
            bttn.draw(screen, hover=hover)

        # Draw title
        font = pygame.font.Font(None, 74)
        text = font.render("Pause", True, (0, 0, 0))
        text_rect = text.get_rect(center=(pause_screen.posx + pause_screen.rect.width // 2, pause_screen.posy+ 50))
        screen.blit(text, text_rect)

        pygame.display.update()

def game_loop():
    running = True
    clock = pygame.time.Clock()
    state = "menu"
    while running:
        clock.tick(60)  # Limit frame rate to 60 FPS
        screen.fill(DESERT)
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
            result = pause_game(screen, snapshot)
            if result == "resume":
                snapshot = screen.copy()
                state = "load_game"
            else:
                state = result

            
        pygame.display.flip()

    pygame.quit()


# Run the game
game_loop()
