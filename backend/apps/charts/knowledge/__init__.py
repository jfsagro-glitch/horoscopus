from .venus import VENUS_KNOWLEDGE
from .mars import MARS_KNOWLEDGE
from .jupiter import JUPITER_KNOWLEDGE
from .saturn import SATURN_KNOWLEDGE
from .uranus import URANUS_KNOWLEDGE
from .neptune import NEPTUNE_KNOWLEDGE
from .pluto import PLUTO_KNOWLEDGE
from .integral_indicators import INTEGRAL_INDICATORS_KNOWLEDGE

PLANET_KNOWLEDGE = {
    "venus": VENUS_KNOWLEDGE,
    "mars": MARS_KNOWLEDGE,
    "jupiter": JUPITER_KNOWLEDGE,
    "saturn": SATURN_KNOWLEDGE,
    "uranus": URANUS_KNOWLEDGE,
    "neptune": NEPTUNE_KNOWLEDGE,
    "pluto": PLUTO_KNOWLEDGE,
}

__all__ = [
    "PLANET_KNOWLEDGE",
    "VENUS_KNOWLEDGE",
    "MARS_KNOWLEDGE",
    "JUPITER_KNOWLEDGE",
    "SATURN_KNOWLEDGE",
    "URANUS_KNOWLEDGE",
    "NEPTUNE_KNOWLEDGE",
    "PLUTO_KNOWLEDGE",
    "INTEGRAL_INDICATORS_KNOWLEDGE",
]

