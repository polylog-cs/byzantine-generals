import logging
import random
import sys
from typing import Literal, Optional

import manim
from manim import *
from manim import config
from rich.logging import RichHandler

############### DEFAULT OPTIONS

random.seed(0)


def default():
    VMobject.set_default(color=GRAY)
    Polygon.set_default(color=RED)
    # Tex.set_default(color = text_color)
    # Text.set_default(color = text_color)
    # config.text_color = text_color
    # SurroundingRectangle.set_default(color = RED)
    # SurroundingRectangle.set_default(fill_color = config.background_color)
    # SurroundingRectangle.set_default(fill_opacity = 1)


def disable_rich_logging():
    """Disable Manim's Rich-based logger because it's annoying.

    Manim uses the Python package Rich to format its logs.
    It tries to split lines nicely, but then it also splits file paths and then you can't
    command-click them to open them in the terminal.
    """
    # It seems that manim only has the rich handler, but let's remove it specifically
    # in case any file handlers are added under some circumstances.
    for handler in manim.logger.handlers:
        if isinstance(handler, RichHandler):
            manim.logger.handlers.remove(handler)

    ANSI_DARK_GRAY = "\033[1;30m"
    ANSI_END = "\033[0m"

    # Add a new handler with a given format. Note that the removal above is still needed
    # because otherwise we get two copies of the same log messages.
    logging.basicConfig(
        format=f"{ANSI_DARK_GRAY}%(asctime)s %(levelname)s{ANSI_END} %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


############### GENERATING SOUNDS

SoundEffect = Literal["lovely", "click", "pop", "explosion"]

SOUND_EFFECTS = {
    "lovely": ("audio/lovely/lovely_{}.wav", 7),
    "click": ("audio/click/click_{}.wav", 4),
    "pop": ("audio/pop/pop_{}.wav", 7),
    "explosion": ("audio/explosion/explosion_{}.wav", 3),
    "whoosh": ("audio/whoosh/whoosh_{}.wav", 4),
}

assert typing.get_args(SoundEffect) == tuple(
    SOUND_EFFECTS.keys()
), "Ensure that SoundEffect and SOUND_EFFECTS are in sync"


def get_sound_effect(
    name: SoundEffect,
    rng: Optional[np.random.Generator] = None,
    variant: Optional[int] = None,
):
    """Return a sound effect with the given name.

    Args:
        name: The name of the sound effect.
        rng: The random number generator to use for reproducibility.
        variant: if set, return the exact variant of this sound effect
            instead of selecting randomly.
    """
    assert (
        name in SOUND_EFFECTS
    ), f"Unknown sound effect {name}. Valid options: {SOUND_EFFECTS.keys()}"
    path, n_variants = SOUND_EFFECTS[name]

    if variant is None:
        rng = rng or np.random.default_rng()
        return path.format(rng.integers(0, n_variants))
    else:
        assert rng is None, "`rng` and `variant` cannot both be set"
        assert 0 <= variant < n_variants
        return path.format(variant)


############### ANIMATIONS


def arrive_from(obj, dir, buff=0.5):
    pos = obj.get_center()
    obj.align_to(Point().to_edge(dir, buff=0), -dir).shift(buff * dir)
    return obj.animate.move_to(pos)


############### SOLARIZED COLORS


# background tones (dark theme)

BASE03 = "#002b36"
BASE02 = "#073642"
BASE01 = "#586e75"

# content tones

BASE00 = "#657b83"
BASE0 = "#839496"
BASE1 = "#93a1a1"

# background tones (light theme)

BASE2 = "#eee8d5"
BASE3 = "#fdf6e3"

# accent tones

YELLOW = "#d0b700"
YELLOW2 = "#b58900"  # The original Solarized yellow
ORANGE = "#c1670c"
ORANGE2 = "#cb4b16"  # The original Solarized orange - too close to red
RED = "#dc322f"
MAGENTA = "#d33682"
VIOLET = "#6c71c4"
BLUE = "#268bd2"
CYAN = "#2aa198"
CYAN2 = "#008080"
GREEN = "#859900"
HIGHLIGHT = YELLOW2

# Alias
GRAY = BASE00
GREY = BASE00

text_color = GRAY
TEXT_COLOR = GRAY
DALLE_ORANGE = r"#%02x%02x%02x" % (254, 145, 4)

# whenever more colors are needed
rainbow = [RED, MAGENTA, VIOLET, BLUE, CYAN, GREEN]
# [RED, ORANGE, GREEN, TEAL, BLUE, VIOLET, MAGENTA]
# [GREEN, TEAL, BLUE, VIOLET, MAGENTA, RED, ORANGE]


config.background_color = BASE2
BACKGROUND_COLOR_LIGHT = BASE2
BACKGROUND_COLOR_DARK = BASE02
BACKGROUND_COLOR = BACKGROUND_COLOR_LIGHT

config.max_files_cached = 1000


class SendMessage(Animation):
    def __init__(self, mobject: Mobject, start, end, **kwargs) -> None:
        super().__init__(mobject, **kwargs)
        self.start = start
        self.end = end

    def interpolate_mobject(self, alpha: float) -> None:
        alpha = rate_functions.ease_in_out_sine(alpha)
        scale = rate_functions.there_and_back_with_pause(alpha)

        self.mobject.scale_to_fit_width(0.01 + scale * 0.8)
        self.mobject.move_to(self.start + alpha * (self.end - self.start))

        if alpha == 1.0:
            # The scale needs to be non-zero at all times, so make the
            # mobject transparent at the end to
            self.mobject.set_opacity(0)
