import os
import random
import sys
import time

RESET = "\033[0m"
BOLD = "\033[1m"

GRADIENT = [
    "\033[91m",
    "\033[93m",
    "\033[96m",
    "\033[95m",
    "\033[92m",
    "\033[94m",
]


def typewriter_effect(text: str, delay: float = 0.03) -> None:
    """Display text with a colored typewriter effect.

    Prints each character one at a time with a random color chosen from
    GRADIENT and a short sleep between characters.

    Args:
        text:  The string to display character by character.
        delay: Seconds to wait between each character (default 0.03).
    """
    for char in text:
        color = random.choice(GRADIENT)
        sys.stdout.write(f"{BOLD}{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def simple_loading(total: int = 40, speed: float = 0.04) -> None:
    """Display a simple animated loading bar in the terminal.

    Prints a progress bar that fills from left to right using block
    characters, updating in place with carriage returns.

    Args:
        total: Number of steps (bar segments) in the loading animation.
        speed: Seconds to wait between each step update (default 0.04).
    """
    color = random.choice(GRADIENT)
    print(f"{BOLD}{color}Initializing Maze Portal...{RESET}")
    for index in range(total + 1):
        filled = f"{color}█{RESET}" * index
        empty = f"{color}─{RESET}" * (total - index)
        percent = f"{color}{index * 100 // total}%{RESET}"
        sys.stdout.write(f"\r[{filled}{empty}] {percent}")
        sys.stdout.flush()
        time.sleep(speed)
    print(f"\n{BOLD}{color}✓ Portal Stabilized ✓{RESET}\n")


def intro_screen() -> None:
    """Show the full startup animation sequence before the maze appears.

    Clears the terminal, then sequentially displays:
      1. A large ASCII-art 'MASÉEV' title, one line at a time.
      2. A typewriter-effect subtitle crediting the authors.
      3. An animated loading bar.
      4. A 'MAZE READY' banner.
      5. A 'Press ENTER to start' prompt.

    Clears the terminal again after the user presses Enter so the maze
    is displayed on a clean screen.
    """
    os.system("cls" if os.name == "nt" else "clear")

    title = [
        " ███╗   ███╗ █████╗ ███████╗███████╗██╗   ██╗",
        " ████╗ ████║██╔══██╗██╔════╝██╔════╝██║   ██║",
        " ██╔████╔██║███████║███████╗█████╗  ██║   ██║",
        " ██║╚██╔╝██║██╔══██║╚════██║██╔══╝  ╚██╗ ██╔╝",
        " ██║ ╚═╝ ██║██║  ██║███████║███████╗ ╚████╔╝ ",
        " ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝  ╚═══╝  ",
        "",
        "           MAZE PORTAL",
    ]

    for index, line in enumerate(title):
        color = GRADIENT[index % len(GRADIENT)]
        print(f"{BOLD}{color}{line}{RESET}")
        time.sleep(0.08)

    typewriter_effect("🎮 A-Maze-ing by Mery & Manar 🎮", delay=0.05)
    simple_loading()
    print(f"{BOLD}{random.choice(GRADIENT)}⚡ MAZE READY ⚡{RESET}")
    input(f"{random.choice(GRADIENT)}Press ENTER to start...{RESET}")
    os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    intro_screen()
