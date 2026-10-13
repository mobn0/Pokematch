"""PokeMatch logic – FUNCTIONAL implementation.

Rules for this file:
  - no mutation: no list.append, no reassigning accumulators, no for/while loops
  - use filter / map / functools.reduce / sorted, lambdas, comprehensions
  - pass functions around as values (first-class functions)
  - return tuples (immutable), never lists

Must have exactly the same functions/signatures as imperative.py.
"""

from functools import reduce
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
    return tuple(filter(
        lambda p: not generations or p.generation in generations,
        pokemon,
    ))


def filter_by_types(
    pokemon: Sequence[Pokemon], wanted_types: Collection[str]
) -> tuple[Pokemon, ...]:
    """Keep only Pokémon that have AT LEAST ONE of `wanted_types`.

    Empty `wanted_types` -> keep all.

    >>> filter_by_types((charmander, squirtle), {"fire", "grass"})
    (charmander,)
    """
    return tuple(filter(
        lambda p: not wanted_types
        or reduce(lambda found, t: found or t in wanted_types, p.types, False),
        pokemon,
    ))


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
    stat_part = sum(
        map(lambda name: getattr(p.stats, name) * profile.stat_weights.get(name, 0), STAT_NAMES)
    )
    matches = len(tuple(filter(lambda t: t in profile.types, p.types)))
    return float(stat_part + profile.type_bonus * matches)


def score_all(
    pokemon: Sequence[Pokemon], profile: Profile
) -> tuple[ScoredPokemon, ...]:
    """Map every Pokémon to ScoredPokemon(pokemon, fit_score(pokemon, profile)).

    Order stays the same as the input.
    """
    return tuple(map(lambda p: ScoredPokemon(p, fit_score(p, profile)), pokemon))


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
    if not scored:
        return ()
    lo, hi = reduce(
        lambda acc, s: (min(acc[0], s.score), max(acc[1], s.score)),
        scored,
        (scored[0].score, scored[0].score),
    )
    scale = lambda score: 100.0 if hi == lo else round((score - lo) / (hi - lo) * 100, 1)
    return tuple(map(lambda s: ScoredPokemon(s.pokemon, scale(s.score)), scored))


def rank(scored: Sequence[ScoredPokemon], limit: int) -> tuple[ScoredPokemon, ...]:
    """Sort by score descending (ties: by name ascending) and keep the top `limit`."""
    return tuple(sorted(scored, key=lambda s: (-s.score, s.pokemon.name))[:limit])


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
    return rank(
        normalize_scores(
            score_all(
                filter_by_types(filter_by_generation(pokemon, generations), profile.types),
                profile,
            )
        ),
        limit,
    )
