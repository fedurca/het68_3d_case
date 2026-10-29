"""Headless shaded renders. No display and no browser."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def _tessellate(part, tolerance=0.45):
    verts, tris = part.tessellate(tolerance)
    v = np.array([(p.X, p.Y, p.Z) for p in verts], dtype=np.float64)
    t = np.array(tris, dtype=np.int32)
    return v, t


def _normalize(v):
    n = np.linalg.norm(v)
    return v / n if n else v


def render_views(colored_parts, out_dir: Path, stem: str, views: dict):
    meshes = []
    for part, color in colored_parts:
        v, t = _tessellate(part)
        if len(t) == 0:
            continue
        meshes.append((v, t, np.array(color, dtype=np.float64)))
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, (eye, up) in views.items():
        img = _raster(meshes, np.array(eye, dtype=np.float64), np.array(up, dtype=np.float64))
        img.save(out_dir / f"{stem}-{name}.png")


def render_part(part, color, path: Path):
    v, t = _tessellate(part, tolerance=0.4)
    img = _raster(
        [(v, t, np.array(color, dtype=np.float64))],
        np.array((1.0, -0.7, 0.55)),
        np.array((0.0, 0.0, 1.0)),
        size=800,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def _raster(meshes, eye, up, size=1000):
    eye = _normalize(eye)
    up = _normalize(up)
    z_cam = eye
    x_cam = _normalize(np.cross(up, z_cam))
    y_cam = np.cross(z_cam, x_cam)

    all_v = np.vstack([v for v, _, _ in meshes])
    cam = np.column_stack(
        [
            all_v @ x_cam,
            all_v @ y_cam,
            all_v @ z_cam,
        ]
    )
    span = max(cam[:, 0].max() - cam[:, 0].min(), cam[:, 1].max() - cam[:, 1].min(), 1.0)
    scale = (size * 0.82) / span
    mid = cam[:, :2].mean(axis=0)
    light = _normalize(eye + np.array((0.2, 0.3, 0.8)))

    zbuf = np.full((size, size), -1e18, dtype=np.float32)
    rgb = np.full((size, size, 3), 244, dtype=np.uint8)

    for verts, tris, color in meshes:
        p = np.column_stack((verts @ x_cam, verts @ y_cam, verts @ z_cam))
        scr = np.empty((len(p), 2), dtype=np.float64)
        scr[:, 0] = (p[:, 0] - mid[0]) * scale + size / 2
        scr[:, 1] = size / 2 - (p[:, 1] - mid[1]) * scale
        depth = p[:, 2]
        n = np.cross(verts[tris[:, 1]] - verts[tris[:, 0]], verts[tris[:, 2]] - verts[tris[:, 0]])
        nn = np.linalg.norm(n, axis=1)
        nn[nn == 0] = 1.0
        n /= nn[:, None]
        shade = np.clip(n @ light, 0, 1)
        facing = n @ z_cam
        shade = np.where(facing >= 0, 0.25 + 0.75 * shade, 0.12 + 0.25 * shade)
        col = (np.clip(color[None, :] * shade[:, None], 0, 1) * 255).astype(np.uint8)
        for i in range(len(tris)):
            pts = scr[tris[i]]
            minx = max(int(pts[:, 0].min()), 0)
            maxx = min(int(pts[:, 0].max()) + 1, size)
            miny = max(int(pts[:, 1].min()), 0)
            maxy = min(int(pts[:, 1].max()) + 1, size)
            if minx >= maxx or miny >= maxy:
                continue
            area = (pts[1, 0] - pts[0, 0]) * (pts[2, 1] - pts[0, 1]) - (pts[1, 1] - pts[0, 1]) * (
                pts[2, 0] - pts[0, 0]
            )
            if abs(area) < 1e-6:
                continue
            gx = np.arange(minx, maxx, dtype=np.float32) + 0.5
            gy = np.arange(miny, maxy, dtype=np.float32) + 0.5
            X, Y = np.meshgrid(gx, gy)
            w0 = ((pts[1, 0] - X) * (pts[2, 1] - Y) - (pts[1, 1] - Y) * (pts[2, 0] - X)) / area
            w1 = ((pts[2, 0] - X) * (pts[0, 1] - Y) - (pts[2, 1] - Y) * (pts[0, 0] - X)) / area
            w2 = 1.0 - w0 - w1
            mask = (w0 >= -0.01) & (w1 >= -0.01) & (w2 >= -0.01)
            if not mask.any():
                continue
            z = w0 * depth[tris[i, 0]] + w1 * depth[tris[i, 1]] + w2 * depth[tris[i, 2]]
            view = zbuf[miny:maxy, minx:maxx]
            update = mask & (z > view)
            if not update.any():
                continue
            view[update] = z[update]
            ys, xs = np.nonzero(update)
            rgb[miny + ys, minx + xs] = col[i]
    return Image.fromarray(rgb, mode="RGB")
