"""PokeMatch logic – IMPERATIVE implementation.

Rules for this file:
  - classic for-loops, if-statements, local variables
  - build results by mutating a list (result.append(...)), then return tuple(result)
  - accumulators for min/max/sum instead of reduce

Must have exactly the same functions/signatures as functional.py.
"""

from typing import Collection, Sequence

from backend.models import STAT_NAMES, Pokemon, Profile, ScoredPokemon


def filter_by_generation(
    pokemon: Sequence[Pokemon], generations: Collection[int]
) -> tuple[Pokemon, ...]:
    """Keep only Pokémon whose `generation` is in `generations`.

    Reduces the data cube to the wanted layer(s).
    Empty `generations` -> keep all.

    >>> filter_by_generation((bulbasaur_g1, chikorita_g2), {1})
    (bulbasaur_g1,)
    """
    raise NotImplementedError("filter_by_generation")


def filter_by_types(
    pokemon: Sequence[Pokemon], wanted_types: Collection[str]
) -> tuple[Pokemon, ...]:
    """Keep only Pokémon that have AT LEAST ONE of `wanted_types`.

    Empty `wanted_types` -> keep all.

    >>> filter_by_types((charmander, squirtle), {"fire", "grass"})
    (charmander,)
    """
    raise NotImplementedError("filter_by_types")


def fit_score(p: Pokemon, profile: Profile) -> float:
    """Raw (not normalised) fit-score of one Pokémon.

    score = sum(base_stat * weight for every stat in STAT_NAMES)
          + profile.type_bonus * (number of p.types that are in profile.types)

    Stats missing from `profile.stat_weights` count as weight 0.
    Read a stat by name with getattr(p.stats, name).

    >>> fit_score(charmander, Profile(types=frozenset({"fire"}),
    ...                               stat_weights={"attack": 2, "speed": 1}))
    52*2 + 65*1 + 50*1  ==  219.0
    """
    raise NotImplementedError("fit_score")


def score_all(
    pokemon: Sequence[Pokemon], profile: Profile
) -> tuple[ScoredPokemon, ...]:
    """Map every Pokémon to ScoredPokemon(pokemon, fit_score(pokemon, profile)).

    Order stays the same as the input.
    """
    raise NotImplementedError("score_all")


def normalize_scores(
    scored: Sequence[ScoredPokemon],
) -> tuple[ScoredPokemon, ...]:
    """Rescale all scores to 0–100 (min-max normalisation), rounded to 1 decimal.

    1. find min and max score (reduce)
    2. new = (score - min) / (max - min) * 100 (map)

    Edge cases:
      - empty input            -> ()
      - all scores equal       -> every score becomes 100.0
    Order stays the same as the input.
    """
    raise NotImplementedError("normalize_scores")


def rank(scored: Sequence[ScoredPokemon], limit: int) -> tuple[ScoredPokemon, ...]:
    """Sort by score descending (ties: by name ascending) and keep the top `limit`."""
    raise NotImplementedError("rank")


def find_best_matches(
    pokemon: Sequence[Pokemon],
    generations: Collection[int],
    profile: Profile,
    limit: int,
) -> tuple[ScoredPokemon, ...]:
    """The whole pipeline:

    filter_by_generation -> filter_by_types(profile.types) -> score_all
    -> normalize_scores -> rank(limit)
    """
    raise NotImplementedError("find_best_matches")
