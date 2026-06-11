"""Small profiling helpers for smoke and integration scripts."""

from __future__ import annotations

from collections.abc import Iterator, MutableMapping
from contextlib import contextmanager
from time import perf_counter


class StageTimer:
    """Record wall-clock seconds for named stages using time.perf_counter."""

    def __init__(self, timings_s: MutableMapping[str, float] | None = None) -> None:
        self.timings_s: MutableMapping[str, float] = timings_s if timings_s is not None else {}

    @contextmanager
    def stage(self, name: str) -> Iterator[None]:
        start = perf_counter()
        try:
            yield
        finally:
            elapsed = perf_counter() - start
            self.timings_s[name] = float(self.timings_s.get(name, 0.0) + elapsed)

    def as_dict(self) -> dict[str, float]:
        return dict(self.timings_s)


@contextmanager
def timer_stage(timings_s: MutableMapping[str, float], name: str) -> Iterator[None]:
    with StageTimer(timings_s).stage(name):
        yield
