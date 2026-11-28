"""Equivalencia entre la deteccion de cruces de I3 y la de I2 (``domain/course_index/conflicts``).

Ambas implementan el mismo contrato (dia 0=lunes, minutos [inicio, fin)); esta prueba comprueba
que dan la misma respuesta para reuniones y ofertas aleatorias, incluidos los bordes
(fin == inicio de la otra reunion no es cruce).
"""

from __future__ import annotations

import random
import unittest

from domain.scheduling import Meeting, Offering, meetings_overlap, offerings_conflict

try:
    from domain.course_index.conflicts import Interval, conflicts, overlaps

    MISSING = None
except ImportError as exc:  # pragma: no cover
    MISSING = str(exc)


def rand_meeting(rng: random.Random) -> Meeting:
    day = rng.randrange(0, 2)  # pocos dias y franja corta: muchos cruces y bordes
    start = rng.randrange(480, 840, 30)
    return Meeting(day, start, min(1440, start + rng.choice((30, 60, 90))))


def offering(nrc: str, meetings) -> Offering:
    return Offering("T", nrc, "SYN001", "1", "Docente sintetico", tuple(meetings), "sintetico",
                    "2026-01-01T00:00:00Z")


def to_interval(m: Meeting) -> "Interval":
    return Interval(m.day, m.start_minute, m.end_minute)


@unittest.skipIf(MISSING, f"requiere domain.course_index.conflicts de I2: {MISSING}")
class ConflictEquivalenceTests(unittest.TestCase):
    def test_meeting_pairs_including_borders(self):
        rng = random.Random(20261127)
        seen = {True: 0, False: 0, "borde": 0}
        for _ in range(5000):
            a, b = rand_meeting(rng), rand_meeting(rng)
            expected = overlaps(to_interval(a), to_interval(b))
            self.assertEqual(meetings_overlap(a, b), expected, (a, b))
            self.assertEqual(meetings_overlap(a, b), meetings_overlap(b, a))
            seen[expected] += 1
            seen["borde"] += a.day == b.day and (a.end_minute == b.start_minute
                                                 or b.end_minute == a.start_minute)
        self.assertGreater(seen[True], 300)
        self.assertGreater(seen[False], 300)
        self.assertGreater(seen["borde"], 50)

    def test_offerings(self):
        rng = random.Random(7)
        hits = 0
        for i in range(3000):
            left = [rand_meeting(rng) for _ in range(rng.randint(1, 3))]
            right = [rand_meeting(rng) for _ in range(rng.randint(1, 3))]
            expected = conflicts([to_interval(m) for m in left], [to_interval(m) for m in right])
            self.assertEqual(offerings_conflict(offering("1", left), offering("2", right)), expected)
            hits += expected
        self.assertGreater(hits, 100)


if __name__ == "__main__":
    unittest.main()
