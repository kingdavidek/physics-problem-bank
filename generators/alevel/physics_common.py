"""Shared helpers for A-level physics split modules."""
import random


def _sample_variants(pool, count):
    if count >= len(pool):
        picked = pool[:]
        random.shuffle(picked)
        return picked
    return random.sample(pool, count)

