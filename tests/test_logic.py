"""Same tests for both implementations.  Run with:  pytest -v"""

import inspect

import pytest

from backend import functional, imperative
from backend.models import Pokemon, Profile, ScoredPokemon, Stats

IMPLEMENTATIONS = [functional, imperative]
FUNCTIONS = [
    "filter_by_generation", "filter_by_types", "fit_score", "score_all",
    "normalize_scores", "rank", "find_best_matches",
]

#                                             hp atk def spa spd spe
BULBASAUR = Pokemon(1, "bulbasaur", 1, ("grass", "poison"), Stats(45, 49, 49, 65, 65, 45))
CHARMANDER = Pokemon(4, "charmander", 1, ("fire",), Stats(39, 52, 43, 60, 50, 65))
SQUIRTLE = Pokemon(7, "squirtle", 1, ("water",), Stats(44, 48, 65, 50, 64, 43))
CHIKORITA = Pokemon(152, "chikorita", 2, ("grass",), Stats(45, 49, 65, 49, 65, 45))
CYNDAQUIL = Pokemon(155, "cyndaquil", 2, ("fire",), Stats(39, 52, 43, 60, 50, 65))
ALL = (BULBASAUR, CHARMANDER, SQUIRTLE, CHIKORITA, CYNDAQUIL)

PROFILE = Profile(types=frozenset({"fire", "grass"}), stat_weights={"attack": 2, "speed": 1})


def names(items) -> list[str]:
    return [(i.pokemon if isinstance(i, ScoredPokemon) else i).name for i in items]


# --- contract -------------------------------------------------------------

@pytest.mark.parametrize("fn", FUNCTIONS)
def test_same_signatures(fn):
    assert inspect.signature(getattr(functional, fn)) == inspect.signature(getattr(imperative, fn))


# --- filter_by_generation -------------------------------------------------

@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_filter_by_generation(logic):
    assert logic.filter_by_generation(ALL, {2}) == (CHIKORITA, CYNDAQUIL)
    assert logic.filter_by_generation(ALL, {1, 2}) == ALL
    assert logic.filter_by_generation(ALL, {3}) == ()


@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_filter_by_generation_empty_keeps_all(logic):
    assert logic.filter_by_generation(ALL, []) == ALL


# --- filter_by_types ------------------------------------------------------

@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_filter_by_types(logic):
    assert logic.filter_by_types(ALL, {"fire"}) == (CHARMANDER, CYNDAQUIL)
    assert logic.filter_by_types(ALL, {"poison", "water"}) == (BULBASAUR, SQUIRTLE)
    assert logic.filter_by_types(ALL, {"dragon"}) == ()


@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_filter_by_types_empty_keeps_all(logic):
    assert logic.filter_by_types(ALL, []) == ALL


# --- fit_score ------------------------------------------------------------

@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_fit_score(logic):
    assert logic.fit_score(CHARMANDER, PROFILE) == pytest.approx(52 * 2 + 65 + 50)   # 219
    assert logic.fit_score(SQUIRTLE, PROFILE) == pytest.approx(48 * 2 + 43)          # 139, no type match
    two_types = Profile(types=frozenset({"grass", "poison"}), type_bonus=10)
    assert logic.fit_score(BULBASAUR, two_types) == pytest.approx(20)                # 2 matches, no weights


# --- score_all ------------------------------------------------------------

@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_score_all(logic):
    result = logic.score_all((CHARMANDER, SQUIRTLE), PROFILE)
    assert isinstance(result, tuple)
    assert result == (ScoredPokemon(CHARMANDER, 219), ScoredPokemon(SQUIRTLE, 139))


# --- normalize_scores -----------------------------------------------------

@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_normalize_scores(logic):
    scored = (ScoredPokemon(BULBASAUR, 10), ScoredPokemon(CHARMANDER, 30), ScoredPokemon(SQUIRTLE, 20))
    result = logic.normalize_scores(scored)
    assert [s.score for s in result] == [0.0, 100.0, 50.0]
    assert names(result) == ["bulbasaur", "charmander", "squirtle"]


@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_normalize_scores_rounds_to_one_decimal(logic):
    scored = (ScoredPokemon(BULBASAUR, 0), ScoredPokemon(CHARMANDER, 1), ScoredPokemon(SQUIRTLE, 3))
    assert [s.score for s in logic.normalize_scores(scored)] == [0.0, 33.3, 100.0]


@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_normalize_scores_edge_cases(logic):
    assert logic.normalize_scores(()) == ()
    same = (ScoredPokemon(BULBASAUR, 7), ScoredPokemon(CHARMANDER, 7))
    assert [s.score for s in logic.normalize_scores(same)] == [100.0, 100.0]


@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_normalize_does_not_mutate_input(logic):
    scored = (ScoredPokemon(BULBASAUR, 10), ScoredPokemon(CHARMANDER, 30))
    logic.normalize_scores(scored)
    assert scored == (ScoredPokemon(BULBASAUR, 10), ScoredPokemon(CHARMANDER, 30))


# --- rank -----------------------------------------------------------------

@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_rank(logic):
    scored = (
        ScoredPokemon(SQUIRTLE, 50), ScoredPokemon(CYNDAQUIL, 100),
        ScoredPokemon(BULBASAUR, 0), ScoredPokemon(CHARMANDER, 100),
    )
    assert names(logic.rank(scored, 10)) == ["charmander", "cyndaquil", "squirtle", "bulbasaur"]
    assert names(logic.rank(scored, 2)) == ["charmander", "cyndaquil"]


# --- find_best_matches (whole pipeline) -----------------------------------

@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_find_best_matches(logic):
    # gen 1 + fire/grass -> bulbasaur (193), charmander (219) -> normalised 0 / 100
    result = logic.find_best_matches(ALL, {1}, PROFILE, 10)
    assert [(s.pokemon.name, s.score) for s in result] == [("charmander", 100.0), ("bulbasaur", 0.0)]


@pytest.mark.parametrize("logic", IMPLEMENTATIONS)
def test_find_best_matches_limit(logic):
    result = logic.find_best_matches(ALL, [], Profile(stat_weights={"defense": 1}), 2)
    assert names(result) == ["chikorita", "squirtle"]


def test_both_implementations_agree():
    profile = Profile(types=frozenset({"fire", "water"}), stat_weights={"hp": 1, "special_attack": 1.5})
    assert functional.find_best_matches(ALL, [], profile, 10) == imperative.find_best_matches(ALL, [], profile, 10)
