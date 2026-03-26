# file: maze/intro_animation.py
import time
import sys
import os
import random

# Couleurs et style
RESET = "\033[0m"
BOLD = "\033[1m"

# Gradient colors
GRADIENT = [
    "\033[91m",  # Bright red
    "\033[93m",  # Bright yellow
    "\033[96m",  # Bright cyan
    "\033[95m",  # Bright magenta
    "\033[92m",  # Bright green
    "\033[94m",  # Bright blue
]


def typewriter_effect(text, delay=0.03):
    """Typewriter effect avec couleurs gradient pour le texte."""
    for char in text:
        color = random.choice(GRADIENT)
        sys.stdout.write(f"{BOLD}{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def simple_loading(total=40, speed=0.04):
    """Loading bar simple, couleur unique tirée au hasard du gradient."""
    color = random.choice(GRADIENT)
    print(f"{BOLD}{color}Initializing Maze Portal...{RESET}")
    for i in range(total + 1):
        filled = f"{color}█{RESET}" * i
        empty = f"{color}─{RESET}" * (total - i)
        percent = f"{color}{i*100//total}%{RESET}"
        sys.stdout.write(f"\r[{filled}{empty}] {percent}")
        sys.stdout.flush()
        time.sleep(speed)
    print(f"\n{BOLD}{color}✓ Portal Stabilized ✓{RESET}\n")


def intro_screen():
    """Intro screen vibrant, loading color unique mais titre gradient."""
    # Clear
    os.system('cls' if os.name == 'nt' else 'clear')

    # Titre ASCII coloré
    title = [
        " ███╗   ███╗ █████╗ ███████╗███████╗██╗   ██╗",
        " ████╗ ████║██╔══██╗██╔════╝██╔════╝██║   ██║",
        " ██╔████╔██║███████║███████╗█████╗  ██║   ██║",
        " ██║╚██╔╝██║██╔══██║╚════██║██╔══╝  ╚██╗ ██╔╝",
        " ██║ ╚═╝ ██║██║  ██║███████║███████╗ ╚████╔╝ ",
        " ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝  ╚═══╝  ",
        "",
        "           MAZE PORTAL"
    ]

    for i, line in enumerate(title):
        color = GRADIENT[i % len(GRADIENT)]
        print(f"{BOLD}{color}{line}{RESET}")
        time.sleep(0.08)

    # Authors
    typewriter_effect("🎮 A-Maze-ing by Mery & Manar 🎮", delay=0.05)

    # Loading simple
    simple_loading()

    # Invite final
    print(f"{BOLD}{random.choice(GRADIENT)}⚡ MAZE READY ⚡{RESET}")
    input(f"{random.choice(GRADIENT)}Press ENTER to start...{RESET}")

    # Clear pour le maze
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    intro_screen()
