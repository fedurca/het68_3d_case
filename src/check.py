"""Checks that do not need a viewer: baselines, envelopes, and mesh sections."""

from __future__ import annotations

import math
import struct
from pathlib import Path

from build123d import Vector

from params import (
    ACOUSTIC_R,
    CELL_H,
    COLLAR_FACE_R,
    COLLAR_OD,
    CORE_BOARD_Z,
    CORE_X,
    CORE_Y,
    EDGE_MM,
    GROOVE_DEPTH,
    HUB_CAV_R,
    HUB_R,
    KEY_HEIGHT,
    LUG_FROM_FACE,
    LUG_RADIAL,
    MAST_SPIGOT,
    MIC_DIR,
    MOUTH_R,
    PIEZO_AXIS_R,
    PIEZO_AZ,
    PIPE_ID,
    POD_SHOULDER,
    PWR_BOARD_Z,
    RJ45_PLUG_H,
    RJ45_PLUG_W,
    SAT_RJ45,
    SEAT_R,
    SOCKET_ID,
    SPIGOT_LEN,
    SPIGOT_OD,
    board_local,
    cable_length,
    mast_mouth_z,
    mast_seat_z,
    opposite_distance,
    stack_points,
)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


def check_baselines():
    for i, raw in enumerate(MIC_DIR):
        n = math.sqrt(sum(c * c for c in raw))
        assert abs(n - 1) < 1e-4, (i, n)
    for i in range(3):
        dist = opposite_distance(i)
        assert abs(dist - EDGE_MM) < 0.05, (i, dist)
        a = _unit(MIC_DIR[i])
        b = _unit(MIC_DIR[i + 1 if i < 2 else 0])
        # 0-1, 1-2 are adjacent; 2 and 0 are also adjacent (upper triangle is
        # orthogonal too: every non-opposite pair is 90 degrees).
    for i in range(6):
        for j in range(i + 1, 6):
            dot = sum(MIC_DIR[i][k] * MIC_DIR[j][k] for k in range(3))
            opposite = (j - i) % 6 == 3
            if opposite:
                assert dot < -0.999, (i, j, dot)
            else:
                assert abs(dot) < 0.01, (i, j, dot)
    assert abs(ACOUSTIC_R - EDGE_MM / 2) < 1e-9
    # The whole stack, including the cell under the power board and the
    # RJ45 bodies on the core, sits inside the spherical cavity.
    for point in stack_points():
        radius = math.sqrt(sum(c * c for c in point))
        assert radius < HUB_CAV_R - 2.0, (point, radius)
    # An RJ45 plug passes the stalk bore and the printed socket.
    plug = math.hypot(RJ45_PLUG_W, RJ45_PLUG_H)
    assert plug < PIPE_ID - 4.0, plug
    assert plug < SOCKET_ID - 4.0, plug
    assert mast_mouth_z() == mast_seat_z() - MAST_SPIGOT
    assert mast_seat_z() < PWR_BOARD_Z - CELL_H - 20.0
    assert cable_length() > ACOUSTIC_R - HUB_CAV_R
    # Bayonet lug and pod slot share one station along the arm.
    arm_tip = COLLAR_FACE_R - SEAT_R
    lug_along = SEAT_R + (arm_tip - LUG_FROM_FACE)
    pod_lug_along = ACOUSTIC_R + (POD_SHOULDER - LUG_FROM_FACE)
    assert abs(lug_along - pod_lug_along) < 0.05, (lug_along, pod_lug_along)
    assert MOUTH_R == SEAT_R + SPIGOT_LEN
    assert COLLAR_OD / 2 + LUG_RADIAL > PIPE_ID / 2
    rib_outer = SPIGOT_OD / 2 + KEY_HEIGHT
    groove_outer = SOCKET_ID / 2 + GROOVE_DEPTH + 0.1
    assert rib_outer < groove_outer, (rib_outer, groove_outer)


def _load_stl(path: Path):
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    assert 84 + n * 50 == len(data), path
    verts = []
    off = 84
    for _ in range(n):
        vals = struct.unpack_from("<12fH", data, off)
        off += 50
        for k in range(3, 12, 3):
            verts.append(vals[k : k + 3])
    return verts


def _section_radii(path: Path, z: float, tol: float = 0.35):
    """Radii of triangle edges crossing the plane z=const."""
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    radii = []
    off = 84
    for _ in range(n):
        vals = struct.unpack_from("<12fH", data, off)
        off += 50
        pts = [vals[3:6], vals[6:9], vals[9:12]]
        hits = []
        for i in range(3):
            j = (i + 1) % 3
            z0, z1 = pts[i][2] - z, pts[j][2] - z
            if abs(z0) < 1e-9:
                hits.append(pts[i])
            elif z0 * z1 < 0:
                t = z0 / (z0 - z1)
                hits.append(tuple(pts[i][k] + t * (pts[j][k] - pts[i][k]) for k in range(3)))
        if len(hits) >= 2:
            for h in hits[:2]:
                radii.append(math.hypot(h[0], h[1]))
    return radii


def _clusters(radii, gap=0.6):
    if not radii:
        return []
    radii = sorted(radii)
    groups = [[radii[0]]]
    for r in radii[1:]:
        if r - groups[-1][-1] > gap:
            groups.append([r])
        else:
            groups[-1].append(r)
    return [sum(g) / len(g) for g in groups if len(g) > 8]


def check_solids(arm_part, hub_lower, hub_upper, pod_part, window_part):
    """Fit checks on the printed solids, before they are meshed."""
    from parts import place
    from params import LED_RING_R, PCB_T, mic_frames as frames_fn

    def inside(part, pt):
        return part.is_inside(tuple(pt), tolerance=1e-3)

    lug_z = (COLLAR_FACE_R - SEAT_R) - LUG_FROM_FACE
    assert inside(arm_part, (0, -(COLLAR_OD / 2 + LUG_RADIAL * 0.5), lug_z))
    assert not inside(arm_part, (0, COLLAR_OD / 2 + LUG_RADIAL * 0.5, lug_z))
    assert not inside(arm_part, (0, 0, 20))
    assert inside(arm_part, (SPIGOT_OD / 2 - 0.4, 0, 20))
    assert not inside(arm_part, (SPIGOT_OD / 2 + 0.5, 0, 20))

    frames = frames_fn()
    for i, frame in enumerate(frames):
        angle = math.degrees(math.acos(max(-1, min(1, frame.n.dot(Vector(*MIC_DIR[i]))))))
        assert angle < 0.5, (i, angle)
        assert (-frame.y).Z < -0.5, i
    # Locked lug of microphone 1 sits on the ground side of the arm.
    seated = place(arm_part, frames[0], SEAT_R)
    lug = frames[0].point(SEAT_R + lug_z, 0, -(COLLAR_OD / 2 + LUG_RADIAL * 0.5))
    assert inside(seated, lug)
    assert lug.Z < frames[0].n.Z * (SEAT_R + lug_z)

    # Microphone port is open; the face beside it and inside the LED circle is closed.
    assert not inside(pod_part, (0, 0, 0.4))
    assert inside(pod_part, (0, 6.2, -0.4))
    assert not inside(pod_part, (LED_RING_R, 0, -0.4))
    assert not inside(window_part, (0, 0, 1.0))
    assert inside(window_part, (LED_RING_R, 0, 0.6))
    # Plug pocket on the ground side of the satellite RJ45 is open, the
    # bud beside it is still closed.
    jx, jy = board_local(*SAT_RJ45)
    assert not inside(pod_part, (jx, jy - 16.0, -8.0))
    assert inside(pod_part, (jx, jy - 16.0, -36.0))

    # Stack center is air. The shell is the same radius along X, Y and Z.
    assert not inside(hub_upper, (40, 30, 20))
    assert not inside(hub_lower, (40, 30, -20))
    assert inside(hub_upper, (0, 0, HUB_R - 3))
    assert not inside(hub_upper, (0, 0, HUB_R + 4))
    assert inside(hub_upper, (HUB_R - 3, 0, 3))
    assert not inside(hub_upper, (HUB_R + 6, 0, 3))
    # Stem socket is open at the mouth and closed before the cavity.
    assert not inside(hub_lower, (0, 0, mast_mouth_z() + 4))
    assert inside(hub_lower, (0, 0, (mast_seat_z() + (-HUB_CAV_R)) / 2))
    for frame in frames:
        half = hub_lower if frame.n.Z < 0 else hub_upper
        assert not inside(half, frame.point((SEAT_R + MOUTH_R) / 2))
    # Posts reach the power board and the core, and stop there.
    assert inside(hub_lower, (69.0, 36.0, PWR_BOARD_Z - 4.0))
    assert not inside(hub_lower, (66.0, 36.0, PWR_BOARD_Z + 6.0))
    assert inside(hub_lower, (-71.0, 44.0, CORE_BOARD_Z - 4.0))
    assert not inside(hub_lower, (-74.0, 44.0, CORE_BOARD_Z + 6.0))
    # The origin, where the two boards face each other, stays empty.
    assert not inside(hub_lower, (0.0, 0.0, 2.0))
    assert not inside(hub_upper, (0.0, 0.0, CORE_BOARD_Z + 4.0))
    # Three piezo holes, 120° apart, open through the lower shell.
    z_out = -math.sqrt(HUB_R**2 - PIEZO_AXIS_R**2)
    z_in = -math.sqrt(HUB_CAV_R**2 - PIEZO_AXIS_R**2)
    z_mid = (z_out + z_in) / 2
    for i, deg in enumerate(PIEZO_AZ):
        a = math.radians(deg)
        x = PIEZO_AXIS_R * math.cos(a)
        y = PIEZO_AXIS_R * math.sin(a)
        assert not inside(hub_lower, (x, y, z_mid))
        assert inside(hub_lower, (x + 7 * math.cos(a), y + 7 * math.sin(a), z_mid))
        nxt = PIEZO_AZ[(i + 1) % len(PIEZO_AZ)]
        assert abs((nxt - deg) % 360 - 120) < 0.1
    # Stack corners are not inside the shell.
    for point in stack_points():
        half = hub_upper if point[2] >= 0 else hub_lower
        assert not inside(half, point), point
    overlap = hub_lower.intersect(hub_upper)
    if overlap is not None:
        solids = overlap.solids() if hasattr(overlap, "solids") else [overlap]
        assert sum(solid.volume for solid in solids) < 1.0


def check_meshes(stl_dir: Path):
    arm = stl_dir / "arm.stl"
    radii = _clusters(_section_radii(arm, 20.0))
    assert any(abs(r - PIPE_ID / 2) < 0.15 for r in radii), radii
    assert any(abs(r - SPIGOT_OD / 2) < 0.15 for r in radii), radii

    # Collar, just behind the outer face. Lug makes one radius larger on -Y.
    tip = COLLAR_FACE_R - SEAT_R
    collar_z = tip - 4.0
    data_r = _section_radii(arm, collar_z)
    clusters = _clusters(data_r)
    assert any(abs(r - PIPE_ID / 2) < 0.2 for r in clusters), clusters
    assert any(abs(r - COLLAR_OD / 2) < 0.35 for r in clusters), clusters

    hub = stl_dir / "hub_lower.stl"
    mouth_z = mast_mouth_z() + 2.0
    hub_r = _clusters(_section_radii(hub, mouth_z))
    assert any(abs(r - SOCKET_ID / 2) < 0.25 for r in hub_r), hub_r

    for name in (
        "hub_lower.stl",
        "hub_upper.stl",
        "arm.stl",
        "pod.stl",
        "pod_window.stl",
        "marks.stl",
    ):
        verts = _load_stl(stl_dir / name)
        assert len(verts) > 30, name
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        zs = [v[2] for v in verts]
        assert max(xs) - min(xs) > 5, name
        assert max(ys) - min(ys) > 5 or name == "marks.stl"
        assert max(zs) - min(zs) > 1, name


def main():
    check_baselines()
    root = Path(__file__).resolve().parents[1]
    check_meshes(root / "export" / "stl")
    print("checks ok")
    print(f"cable length {cable_length():.1f} mm, same on all six arms")


if __name__ == "__main__":
    main()
