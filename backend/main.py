"""PokeMatch – FastAPI backend.

Start:  uvicorn backend.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Choose the implementation here: swap "functional" <-> "imperative"
from backend import functional as logic
# ---------------------------------------------------------------------------

from backend.models import ALL_TYPES, GENERATIONS, STAT_NAMES, Profile
from backend.pokeapi import load_all

logging.basicConfig(level=logging.INFO)

IMPLEMENTATION = logic.__name__.rsplit(".", 1)[-1]

POKEMON: tuple = ()


@asynccontextmanager
async def lifespan(_: FastAPI):
    global POKEMON
    POKEMON = await load_all()
    yield


app = FastAPI(title="PokeMatch", lifespan=lifespan)


class MatchRequest(BaseModel):
    generations: list[int] = Field(default_factory=list, examples=[[1]])
    types: list[str] = Field(default_factory=list, examples=[["fire"]])
    stat_weights: dict[str, float] = Field(default_factory=dict, examples=[{"attack": 2, "speed": 1}])
    type_bonus: float = 50.0
    limit: int = Field(10, ge=1, le=100)

    @field_validator("generations")
    @classmethod
    def _check_generations(cls, v: list[int]) -> list[int]:
        bad = set(v) - set(GENERATIONS)
        if bad:
            raise ValueError(f"unknown generations: {sorted(bad)}")
        return v

    @field_validator("types")
    @classmethod
    def _check_types(cls, v: list[str]) -> list[str]:
        v = [t.lower() for t in v]
        bad = set(v) - set(ALL_TYPES)
        if bad:
            raise ValueError(f"unknown types: {sorted(bad)}")
        return v

    @field_validator("stat_weights")
    @classmethod
    def _check_stats(cls, v: dict[str, float]) -> dict[str, float]:
        bad = set(v) - set(STAT_NAMES)
        if bad:
            raise ValueError(f"unknown stats: {sorted(bad)}")
        return v


@app.get("/api/meta")
def meta() -> dict:
    return {
        "implementation": IMPLEMENTATION,
        "pokemon_loaded": len(POKEMON),
        "generations": list(GENERATIONS),
        "types": list(ALL_TYPES),
        "stats": list(STAT_NAMES),
    }


@app.post("/api/match")
def match(req: MatchRequest) -> dict:
    profile = Profile(
        types=frozenset(req.types),
        stat_weights=req.stat_weights,
        type_bonus=req.type_bonus,
    )
    try:
        best = logic.find_best_matches(POKEMON, req.generations, profile, req.limit)
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail=f"'{e}' is not implemented yet in backend/{IMPLEMENTATION}.py",
        )

    return {
        "implementation": IMPLEMENTATION,
        "results": [[s.pokemon.name, s.score] for s in best],
        "details": [
            {
                "id": s.pokemon.id,
                "name": s.pokemon.name,
                "generation": s.pokemon.generation,
                "types": list(s.pokemon.types),
                "sprite": s.pokemon.sprite,
                "score": s.score,
            }
            for s in best
        ],
    }
