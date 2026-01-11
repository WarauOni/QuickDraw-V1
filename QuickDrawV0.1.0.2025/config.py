import pygame
import os
import sys
import random
import json
from cryptography.fernet import Fernet
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

class Serializable:
    def to_dict(self):
        data = {}
        for key, value in self.__dict__.items():
            if key.startswith("_") or callable(value):
                continue
            if isinstance(value, pygame.Rect):
                data[key] = [value.x, value.y, value.width, value.height]
            elif isinstance(value, pygame.Vector2):
                data[key] = [value.x, value.y]
            elif isinstance(value, pygame.Color):
                data[key] = list(value)
            elif isinstance(value, set):
                data[key] = list(value)
            elif isinstance(value, (list, tuple)) and all(isinstance(i, pygame.Vector2) for i in value):
                data[key] = [[i.x, i.y] for i in value]
            elif isinstance(value, list) and value and hasattr(value[0], "to_dict"):
                data[key] = [v.to_dict() for v in value]
            else:
                data[key] = value
        return data

    @classmethod
    def from_dict(cls, data):
        obj = cls.__new__(cls)  # create an uninitialized instance
        for key, value in data.items():
            if isinstance(value, list):
                # Heuristics to detect type from list structure
                if len(value) == 4 and all(isinstance(i, (int, float)) for i in value):
                    setattr(obj, key, pygame.Rect(*value))
                elif len(value) == 2 and all(isinstance(i, (int, float)) for i in value):
                    setattr(obj, key, pygame.Vector2(*value))
                elif len(value) in (3, 4) and all(isinstance(i, int) for i in value):
                    setattr(obj, key, pygame.Color(*value))
                elif value and isinstance(value[0], list):  # List of vectors
                    setattr(obj, key, [pygame.Vector2(*v) for v in value])
                else:
                    setattr(obj, key, value)
            elif isinstance(value, list):  # Could be a set
                setattr(obj, key, set(value))
            else:
                setattr(obj, key, value)
        return obj


# Function to get the correct path for assets
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev & PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

# Initialize pygame
pygame.init()

# Captions
pygame.display.set_caption("Quick! DRAW!")

# Load and set the window icon
icon_path = resource_path(ASSETS_DIR / "icon.png")
icon = pygame.image.load(icon_path)  # Load icon image
pygame.display.set_icon(icon)  # Set as window icon

# Colors with Hue values (in degrees)
WHITE = (255, 255, 255)  # No hue, neutral color
BLACK = (0, 0, 0)  # No hue, neutral color
RED = (255, 0, 0)  # Hue: 0°
GREEN = (0, 255, 0)  # Hue: 120°
BLUE = (0, 0, 255)  # Hue: 240°
YELLOW = (255, 255, 0)  # Hue: 60°
CYAN = (0, 255, 255)  # Hue: 180°
MAGENTA = (255, 0, 255)  # Hue: 300°
ORANGE = (255, 165, 0)  # Hue: 39°
PURPLE = (128, 0, 128)  # Hue: ~280°
PINK = (255, 192, 203)  # Hue: ~350°
BROWN = (139, 69, 19)  # Hue: ~30°
GRAY = (128, 128, 128)  # Neutral
LIGHT_GRAY = (211, 211, 211)  # Neutral
DARK_GRAY = (64, 64, 64)  # Neutral
DESERT = (193, 154, 107)  # Hue: ~30°

# Fonts
FONT = pygame.font.Font(None, 50)
FONT_PATH = resource_path(ASSETS_DIR / "WEST____.TTF")

# shoot = resource_path("assets/sound/gunshot.mp3")
# buzzer = resource_path("assets/sound/buzzer.wav")

# shoot_sound = pygame.mixer.Sound(shoot)  # Placeholder sound
# buzzer_sound = pygame.mixer.Sound(buzzer) # Placeholder sound


# Get desktop screen size
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Create a fullscreen window
screen = pygame.display.set_mode((SCREEN_WIDTH , SCREEN_HEIGHT), pygame.FULLSCREEN)


# World Building
WORLD_RADIUS = 500  # 5000x5000 world, radius = 2500

MAX_ENEMIES = 50
SPAWN_INTERVAL = 1.0  # seconds


def get_random_spawn_pos(game_container_rect, margin=200):
    side = random.choice(["inside", "top", "bottom", "left", "right"])

    if side == "inside":
        x = random.randint(game_container_rect.left, game_container_rect.right)
        y = random.randint(game_container_rect.top, game_container_rect.bottom)

    elif side == "top":
        x = random.randint(game_container_rect.left, game_container_rect.right)
        y = game_container_rect.top - margin

    elif side == "bottom":
        x = random.randint(game_container_rect.left, game_container_rect.right)
        y = game_container_rect.bottom + margin

    elif side == "left":
        x = game_container_rect.left - margin
        y = random.randint(game_container_rect.top, game_container_rect.bottom)

    elif side == "right":
        x = game_container_rect.right + margin
        y = random.randint(game_container_rect.top, game_container_rect.bottom)

    return x, y




# save_util
save_path = DATA_DIR / "savegame.dat"
save_key = DATA_DIR / "savekey.key"

class GameEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)

# === Only generate once! ===
def generate_key():
    key = Fernet.generate_key()
    with open(save_key, "wb") as f:
        f.write(key)

def load_key():
    return open(save_key, "rb").read()

def encrypt_save(data, filename=save_path):
    key = load_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(data, cls=GameEncoder).encode())
    with open(filename, "wb") as f:
        f.write(encrypted)

def decrypt_load(filename=save_path):
    try:
        key = load_key()
        fernet = Fernet(key)

        with open(filename, "rb") as f:
            encrypted = f.read()

        decrypted = fernet.decrypt(encrypted)
        decoded = decrypted.decode()
        # print("✅ Game Data Loaded:", json.loads(decoded))
        return json.loads(decoded)

    except Exception as e:
        print(f"❌ Decryption/Loading failed: {e}")
        raise  # let the outer function handle it


if not os.path.exists(save_key):
    generate_key()

def save_game_data(player, spawner, items_spawn):
    save_data = {
        "player": player.to_dict(),
        "spawners": spawner.to_dict(),
        "items": items_spawn.to_dict()
    }
    encrypt_save(save_data)
    print("✅ Game saved!")
    return player, spawner, items_spawn


def load_save_data(path=save_path):
    if not os.path.exists(path):
        print("❌ No save file found.")
        return None
    try:
        data = decrypt_load(path)
        # Validate required fields
        if "player" not in data:
            print("❌ Invalid save data: Missing 'player'")
            return None
        # Optional fallback for optional data
        if "bullets" not in data:
            data["bullets"] = []
        return data

    except (json.JSONDecodeError, ValueError) as e:
        print(f"❌ Failed to load save data: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error during load: {e}", repr(e))
        return None

