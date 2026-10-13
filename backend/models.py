"""Shared, immutable domain types used by BOTH logic implementations."""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

STAT_NAMES: tuple[str, ...] = (
    "hp", "attack", "defense", "special_attack", "special_defense", "speed",
)

ALL_TYPES: tuple[str, ...] = (
    "normal", "fire", "water", "electric", "grass", "ice",
    "fighting", "poison", "ground", "flying", "psychic", "bug",
    "rock", "ghost", "dragon", "dark", "steel", "fairy",
)

GENERATIONS: tuple[int, ...] = tuple(range(1, 10))


@dataclass(frozen=True)
class Stats:
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int


@dataclass(frozen=True)
class Pokemon:
    id: int
    name: str
    generation: int
    types: tuple[str, ...]
    stats: Stats
    sprite: str | None = None


@dataclass(frozen=True)
class Profile:
    """What the user is looking for.

    types:        wanted types, e.g. frozenset({"fire", "flying"})
    stat_weights: stat name -> weight, e.g. {"attack": 2.0, "speed": 1.0}
                  (stats not listed count as weight 0)
    type_bonus:   points added per matching type
    """
    types: frozenset[str] = frozenset()
    stat_weights: Mapping[str, float] = field(default_factory=lambda: MappingProxyType({}))
    type_bonus: float = 50.0

    def __post_init__(self) -> None:
        # Make sure the weights can never be mutated after creation.
        object.__setattr__(self, "stat_weights", MappingProxyType(dict(self.stat_weights)))


@dataclass(frozen=True)
class ScoredPokemon:
    pokemon: Pokemon
    score: float
