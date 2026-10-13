"""Live data loading from https://pokeapi.co (I/O lives here, not in the logic files)."""

import asyncio
import logging

import httpx

from backend.models import GENERATIONS, Pokemon, Stats

BASE_URL = "https://pokeapi.co/api/v2"
MAX_PARALLEL = 30

log = logging.getLogger("pokematch")


def _id_from_url(url: str) -> int:
    return int(url.rstrip("/").rsplit("/", 1)[-1])


def _to_pokemon(data: dict, generation: int) -> Pokemon:
    stats = {s["stat"]["name"].replace("-", "_"): s["base_stat"] for s in data["stats"]}
    types = tuple(t["type"]["name"] for t in sorted(data["types"], key=lambda t: t["slot"]))
    return Pokemon(
        id=data["id"],
        name=data["name"],
        generation=generation,
        types=types,
        stats=Stats(**stats),
        sprite=data["sprites"]["front_default"],
    )


async def _get_json(client: httpx.AsyncClient, sem: asyncio.Semaphore, path: str) -> dict:
    async with sem:
        for attempt in range(3):
            try:
                r = await client.get(f"{BASE_URL}/{path}")
                r.raise_for_status()
                return r.json()
            except httpx.HTTPError:
                if attempt == 2:
                    raise
                await asyncio.sleep(1 + attempt)
    raise RuntimeError("unreachable")


async def _load_generation(
    client: httpx.AsyncClient, sem: asyncio.Semaphore, generation: int
) -> list[Pokemon]:
    gen = await _get_json(client, sem, f"generation/{generation}")
    species_ids = [_id_from_url(s["url"]) for s in gen["pokemon_species"]]
    raw = await asyncio.gather(*(_get_json(client, sem, f"pokemon/{i}") for i in species_ids))
    return [_to_pokemon(d, generation) for d in raw]


async def load_all(generations: tuple[int, ...] = GENERATIONS) -> tuple[Pokemon, ...]:
    """Fetch every Pokémon (default form) of the given generations, sorted by id."""
    sem = asyncio.Semaphore(MAX_PARALLEL)
    async with httpx.AsyncClient(timeout=30) as client:
        per_gen = await asyncio.gather(*(_load_generation(client, sem, g) for g in generations))
    all_pokemon = tuple(sorted((p for gen in per_gen for p in gen), key=lambda p: p.id))
    log.info("Loaded %d Pokémon from PokeAPI", len(all_pokemon))
    return all_pokemon
