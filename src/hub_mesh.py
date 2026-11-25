"""Rigid placement of the supplied spojka.

reference/stl/spojka-echo.stl is the hub. The rotation sends the cube's
+X, +Y and +Z ports onto microphones 1, 2 and 3, and the body-diagonal
port onto world −Z. Triangle count, winding and attributes stay as in
the source file. Nothing is remodelled.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from params import MIC_DIR, SPOJK_MAST_MOUTH, SPOJK_MOUTH

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reference" / "stl" / "spojka-echo.stl"

_REC = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")])

# Cube ports, in microphone order 1..6. +X+Y+Z are the upper faces.
_CUBE_AXES = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
    (-1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, -1.0),
)


def rotation() -> np.ndarray:
    """Map cube axes onto MIC_DIR. det = 1.

    Rodrigues sends the body diagonal (1,1,1) to +Z, which leaves +X
    15° west of microphone 1. A +15° twist about Z finishes the match.
    The opposite diagonal stays on −Z because the twist is about Z.
    """
    u = np.ones(3) / math.sqrt(3.0)
    z = np.array([0.0, 0.0, 1.0])
    v = np.cross(u, z)
    s = float(np.linalg.norm(v))
    c = float(np.dot(u, z))
    vx = np.array(
        [[0.0, -v[2], v[1]], [v[2], 0.0, -v[0]], [-v[1], v[0], 0.0]],
        dtype=np.float64,
    )
    r0 = np.eye(3) + vx + vx @ vx * ((1.0 - c) / (s * s))
    ang = math.radians(15.0)
    rz = np.array(
        [
            [math.cos(ang), -math.sin(ang), 0.0],
            [math.sin(ang), math.cos(ang), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    return rz @ r0


def _records(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    n = int(np.frombuffer(raw[80:84], dtype=np.uint32)[0])
    if 84 + n * 50 != len(raw):
        raise ValueError(f"truncated STL: {path}")
    return np.frombuffer(raw[84:], dtype=_REC, count=n).copy()


def source_records() -> np.ndarray:
    return _records(SOURCE)


def placed_records() -> np.ndarray:
    recs = source_records()
    r = rotation()
    recs["n"] = (np.asarray(recs["n"], dtype=np.float64) @ r.T).astype(np.float32)
    recs["v"] = (np.asarray(recs["v"], dtype=np.float64) @ r.T).astype(np.float32)
    return recs


def write_hub(path: Path) -> None:
    """Write the placed mesh. The 80-byte header is copied from the source."""
    recs = placed_records()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as out:
        out.write(SOURCE.read_bytes()[:80])
        out.write(np.uint32(len(recs)).tobytes())
        out.write(recs.tobytes())


def render_arrays() -> tuple[np.ndarray, np.ndarray]:
    """Triangle soup of the placed hub, for the preview raster only."""
    verts = placed_records()["v"].astype(np.float64).reshape(-1, 3)
    tris = np.arange(len(verts), dtype=np.int32).reshape(-1, 3)
    return verts, tris


def assert_exact(path: Path) -> None:
    """The export is the source mesh under rotation(), and the ports match."""
    got = _records(path)
    exp = placed_records()
    if len(got) != len(exp):
        raise AssertionError((len(got), len(exp)))
    if not np.array_equal(got["v"], exp["v"]):
        raise AssertionError("hub vertices differ from the rotated source")
    if not np.array_equal(got["n"], exp["n"]):
        raise AssertionError("hub normals differ from the rotated source")
    if not np.array_equal(got["a"], exp["a"]):
        raise AssertionError("hub attributes differ from the source")

    r = rotation()
    if abs(float(np.linalg.det(r)) - 1.0) > 1e-9:
        raise AssertionError(float(np.linalg.det(r)))
    down = r @ (-np.ones(3) / math.sqrt(3.0))
    if not np.allclose(down, (0.0, 0.0, -1.0), atol=1e-8):
        raise AssertionError(down)

    verts = got["v"].astype(np.float64).reshape(-1, 3)
    for axis, mic in zip(_CUBE_AXES, MIC_DIR):
        world = r @ np.array(axis, dtype=np.float64)
        mic_v = np.array(mic, dtype=np.float64)
        ang = math.degrees(math.acos(float(np.clip(world @ mic_v, -1.0, 1.0))))
        if ang > 0.05:
            raise AssertionError((axis, ang))
        along = verts @ world
        radial = np.linalg.norm(verts - along[:, None] * world, axis=1)
        mouth = float(along[radial < 24.0].max())
        if abs(mouth - SPOJK_MOUTH) > 0.05:
            raise AssertionError((axis, mouth))

    along_down = verts @ np.array([0.0, 0.0, -1.0])
    radial_down = np.linalg.norm(verts - along_down[:, None] * np.array([0.0, 0.0, -1.0]), axis=1)
    mast = float(along_down[radial_down < 26.0].max())
    if abs(mast - SPOJK_MAST_MOUTH) > 0.05:
        raise AssertionError(mast)
