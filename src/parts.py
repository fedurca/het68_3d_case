"""Printable parts for the 384 mm het68 array.

Core and the power board sit at the origin, inside the seven-port hub, so
every satellite cable has the same length. The six arms are one part.
"""

from __future__ import annotations

import math

from build123d import (
    Align,
    Box,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    Rot,
    Vector,
    extrude,
    make_face,
)

from params import (
    ACOUSTIC_R,
    ARROW_LENGTH,
    ARROW_RELIEF,
    BAYONET_TWIST_DEG,
    BOARD_CLEAR,
    BOARD_H,
    BOARD_W,
    COLLAR_FACE_R,
    COLLAR_LEN,
    COLLAR_OD,
    CORE_Y,
    CORE_Z,
    FLANGE_LEN,
    FLANGE_OD,
    GROOVE_DEPTH,
    GROOVE_WIDTH,
    HUB_CAP_Z,
    HUB_CAV_H,
    HUB_CAV_R,
    HUB_FLANGE_R,
    HUB_FLANGE_T,
    HUB_R,
    KEY_HEIGHT,
    KEY_LENGTH,
    KEY_WIDTH,
    LED_RING_R,
    LUG_AXIAL,
    LUG_FROM_FACE,
    LUG_RADIAL,
    LUG_WIDTH,
    MOUNT_HOLES,
    MOUTH_R,
    ORING_CORD,
    PCB_T,
    PIPE_ID,
    PIPE_OD,
    POD_WALL,
    RAIL_CLEAR,
    SCREW_D,
    SEAT_R,
    SOCKET_ID,
    SOCKET_WALL,
    SPIGOT_LEN,
    SPIGOT_OD,
    Frame,
    board_local,
    mast_mouth_z,
    mast_seat_z,
    mic_frames,
)


def _fuse(parts):
    acc = parts[0]
    for part in parts[1:]:
        acc += part
    return acc


def _cut(base, tools):
    acc = base
    for tool in tools:
        acc -= tool
    return acc


def _tube(frame: Frame, z0: float, z1: float, r_out: float, r_in: float):
    """Hollow cylinder along frame.n, from distance z0 to z1 (z1 > z0)."""
    length = z1 - z0
    outer = Cylinder(r_out, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    inner = Pos(0, 0, -1) * Cylinder(
        r_in, length + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
    )
    return frame.plane_at(z0) * (outer - inner)


def _solid_cyl(frame: Frame, z0: float, z1: float, radius: float):
    length = z1 - z0
    body = Cylinder(radius, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return frame.plane_at(z0) * body


def _side_box(frame: Frame, along: float, radial: float, sx: float, sy: float, sz: float):
    """Box centered on the key side (−Y) of the tube, at distance `along`."""
    origin = frame.point(along, 0.0, -radial)
    plane = Plane_from_frame(frame, origin)
    return plane * Box(sx, sy, sz)


def Plane_from_frame(frame: Frame, origin: Vector):
    return Plane(origin=origin, x_dir=frame.x, z_dir=frame.n)


def _clock_box(frame: Frame, delta_deg: float, along: float, radial: float, size):
    """Box on a clock angle. delta 0 is the key side (−Y). Positive twists toward +X."""
    placed = Rot(Z=delta_deg) * Pos(0, -radial, along) * Box(*size)
    # Local +Z of this box is frame.n, local −Y is the key side before the twist.
    return frame.plane_at(0) * placed


def hub_upper():
    """Top half of the central connector. Three microphone sockets."""
    return _hub_half(upper=True)


def hub_lower():
    """Bottom half. Three microphone sockets plus the mast socket on the axis."""
    return _hub_half(upper=False)


def _build_frame() -> Frame:
    """Part-local axes. −Y is the clocking side and maps to world-down on placement."""
    return Frame(Vector(0, 0, 1), Vector(1, 0, 0), Vector(0, 1, 0))


def arm():
    """One microphone boom. The rib and the lug are both on local −Y."""
    frame = _build_frame()
    bore = PIPE_ID / 2
    tip = COLLAR_FACE_R - SEAT_R  # local Z of the collar's outer face
    collar0 = tip - COLLAR_LEN
    parts = [
        _tube(frame, 0, SPIGOT_LEN, SPIGOT_OD / 2, bore),
        _tube(frame, SPIGOT_LEN, SPIGOT_LEN + FLANGE_LEN, FLANGE_OD / 2, bore),
        _tube(frame, SPIGOT_LEN + FLANGE_LEN, collar0, PIPE_OD / 2, bore),
        _tube(frame, collar0, tip, COLLAR_OD / 2, bore),
    ]
    # Clocking rib, proud of the spigot, stopped short of the tip face.
    parts.append(
        _side_box(
            frame,
            KEY_LENGTH / 2 + 1.0,
            SPIGOT_OD / 2 + KEY_HEIGHT / 2,
            KEY_WIDTH,
            KEY_HEIGHT,
            KEY_LENGTH,
        )
    )
    # Bayonet lug on the collar, same clocking as the rib.
    lug_z = tip - LUG_FROM_FACE
    parts.append(
        _side_box(
            frame,
            lug_z,
            COLLAR_OD / 2 + LUG_RADIAL / 2,
            LUG_WIDTH,
            LUG_RADIAL,
            LUG_AXIAL,
        )
    )
    return _fuse(parts)


def _pod_frame() -> Frame:
    return _build_frame()


def _board_center() -> tuple[float, float]:
    x0, y0 = board_local(0.0, 0.0)
    x1, y1 = board_local(BOARD_W, BOARD_H)
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def pod():
    """Satellite head. The acoustic port is the local origin, on the +Z face.

    The board slides in from the hub side and stops on a lip, so nothing
    covers the T5848 port. An L-slot on the collar clocks the RJ45 edge to
    the same side as the arm lug.
    """
    fx0, fy0 = board_local(0.0, 0.0)
    fx1, fy1 = board_local(BOARD_W, BOARD_H)
    cx, cy = _board_center()
    cav_x = BOARD_W + 2 * BOARD_CLEAR
    cav_y = BOARD_H + 2 * BOARD_CLEAR
    outer_x = cav_x + 2 * POD_WALL
    outer_y = cav_y + 2 * POD_WALL
    back = -70.0
    shoulder = -32.0  # collar outer face
    mouth = shoulder - COLLAR_LEN - 2.0
    skirt = mouth - 16.0

    shell = Pos(cx, cy, (0 + back) / 2) * Box(outer_x, outer_y, -back)
    # Board slides in from the hub and stops on the inside of a 1.6 mm front
    # wall. Only the microphone port and the LED ring are open.
    front_inside = -PCB_T
    void = Pos(cx, cy, (back + front_inside) / 2) * Box(
        cav_x, cav_y, (front_inside - back) + 0.05
    )
    mic = Cylinder(3.2, 8, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    # LED ring is open through the front wall. The separate window covers it.
    led_outer = Cylinder(LED_RING_R + 4.2, 6)
    led_inner = Cylinder(LED_RING_R - 4.0, 8)
    led = led_outer - led_inner

    # Socket: skirt grips the tube, then a larger bore holds the collar.
    skirt_bore = Pos(0, 0, (skirt + mouth) / 2) * Cylinder(
        PIPE_OD / 2 + 0.35, mouth - skirt + 0.2
    )
    collar_bore = Pos(0, 0, (mouth + shoulder) / 2) * Cylinder(
        COLLAR_OD / 2 + 0.45, abs(shoulder - mouth) + 0.2
    )
    # Shoulder is the blind end of collar_bore at z=shoulder. Extend it a
    # hair past the shoulder so the boolean face is clean, but not into the
    # board cavity (cavity ends near z=-1.6, shoulder is -32).
    cuts = [void, mic, led, skirt_bore, collar_bore]
    # L-slot. Entry is twisted off the locked angle and runs in from the mouth.
    # The circumferential run ends on the key side, which is the locked pose.
    slot_r = COLLAR_OD / 2 + LUG_RADIAL / 2
    slot_size = (LUG_WIDTH + 2.4, LUG_RADIAL + POD_WALL + 1.0, LUG_AXIAL + 1.6)
    # Hubward of the shoulder is more negative. The lug sits LUG_FROM_FACE
    # behind the collar's outer face.
    lug_z = shoulder - LUG_FROM_FACE
    entry_mid = (mouth - 2 + lug_z) / 2
    entry_h = abs((mouth - 2) - lug_z)
    cuts.append(
        _clock_box(
            _pod_frame(),
            BAYONET_TWIST_DEG,
            entry_mid,
            slot_r,
            (slot_size[0], slot_size[1], entry_h),
        )
    )
    steps = 8
    for i in range(steps + 1):
        delta = BAYONET_TWIST_DEG * (1 - i / steps)
        cuts.append(
            _clock_box(
                _pod_frame(),
                delta,
                lug_z,
                slot_r,
                slot_size,
            )
        )

    body = _cut(shell, cuts)

    # Posts behind the four M3 holes. The board is clamped against the lip.
    posts = []
    for hx, hy in MOUNT_HOLES:
        lx, ly = board_local(hx, hy)
        post = Pos(lx, ly, -8.4) * Cylinder(
            4.2, 10, align=(Align.CENTER, Align.CENTER, Align.CENTER)
        )
        hole = Pos(lx, ly, -8.4) * Cylinder(
            1.6, 11, align=(Align.CENTER, Align.CENTER, Align.CENTER)
        )
        posts.append(post - hole)
        # Rib to the nearest long wall so the post is not floating.
        wall_y = cy + (cav_y / 2) * (1 if ly > cy else -1)
        rib_y = (ly + wall_y) / 2
        rib_len = abs(wall_y - ly) + 2
        posts.append(Pos(lx, rib_y, -7.5) * Box(3.2, rib_len, 6))
    return _fuse([body, *posts])


def pod_window():
    """Translucent cover for the eight SK6812. The centre stays open.

    A flange sits on the pod face and a short spigot drops into the LED
    opening. A low lip around the 6 mm hole takes an open-cell windscreen.
    The web between the lip and the diffuser stays off the microphone port.
    """
    flange = Cylinder(LED_RING_R + 6.0, 1.2) - Cylinder(LED_RING_R - 3.6, 2.0)
    flange = Pos(0, 0, 0.6) * flange
    spigot = Cylinder(LED_RING_R + 3.6, 1.4) - Cylinder(LED_RING_R - 3.6, 2.0)
    spigot = Pos(0, 0, -0.7) * spigot
    web = Cylinder(LED_RING_R - 3.6, 1.2) - Cylinder(4.6, 2.0)
    web = Pos(0, 0, 0.6) * web
    lip = Cylinder(4.6, 3.0) - Cylinder(3.2, 3.6)
    lip = Pos(0, 0, 1.5) * lip
    return flange + spigot + web + lip


def _hub_screws():
    """Six bolts on the equator, between the socket azimuths."""
    radius = HUB_R + 8.0
    holes = []
    span = HUB_FLANGE_T * 2 + 2
    for k in range(6):
        ang = math.radians(30 + 60 * k)
        holes.append(
            Pos(radius * math.cos(ang), radius * math.sin(ang), 0)
            * Cylinder(SCREW_D / 2, span)
        )
    return holes


def _hub_oring():
    """Face groove in the lower flange for a 2.5 mm cord. Opens upward."""
    radius = (HUB_R + HUB_FLANGE_R) / 2
    half_w = ORING_CORD * 0.75
    depth = 1.7
    z = -depth / 2 + 0.25
    outer = Pos(0, 0, z) * Cylinder(radius + half_w, depth + 0.5)
    inner = Pos(0, 0, z) * Cylinder(radius - half_w, depth + 1.6)
    return outer - inner


def _socket_grooves(frames):
    grooves = []
    for frame in frames:
        grooves.append(
            _side_box(
                frame,
                (SEAT_R + MOUTH_R) / 2,
                SOCKET_ID / 2 + GROOVE_DEPTH / 2 - 0.2,
                GROOVE_WIDTH,
                GROOVE_DEPTH + 0.6,
                (MOUTH_R - SEAT_R) + 4,
            )
        )
    return grooves


def _hub_half(upper: bool):
    """Clamshell around the centered stack. Upper and lower each carry three arms."""
    sign = 1.0 if upper else -1.0
    z_outer = HUB_CAP_Z
    z0, z1 = (0.0, z_outer) if upper else (-z_outer, 0.0)
    shell = Pos(0, 0, (z0 + z1) / 2) * Cylinder(HUB_R, z1 - z0)
    flange = Pos(0, 0, sign * HUB_FLANGE_T / 2) * Cylinder(HUB_FLANGE_R, HUB_FLANGE_T)
    flange -= Pos(0, 0, sign * HUB_FLANGE_T / 2) * Cylinder(HUB_R - 0.2, HUB_FLANGE_T + 2)

    frames = mic_frames()[:3] if upper else mic_frames()[3:]
    r_boss = SOCKET_ID / 2 + SOCKET_WALL
    bosses = [_solid_cyl(frame, SEAT_R - 8.0, MOUTH_R, r_boss) for frame in frames]
    parts = [shell, flange, *bosses]
    if not upper:
        seat = mast_seat_z()
        mouth = mast_mouth_z()
        parts.append(Pos(0, 0, (seat + mouth) / 2) * Cylinder(r_boss, seat - mouth))
    body = _fuse(parts)

    cav_h = HUB_CAV_H / 2 + 1.0
    cav_z = sign * (HUB_CAV_H / 4 - 0.5)
    cavity = Pos(0, 0, cav_z) * Cylinder(HUB_CAV_R, cav_h)
    bores = [
        _solid_cyl(frame, SEAT_R - 16.0, MOUTH_R + 1.0, SOCKET_ID / 2) for frame in frames
    ]
    cuts = [cavity, *bores, *_socket_grooves(frames), *_hub_screws()]
    if not upper:
        seat = mast_seat_z()
        mouth = mast_mouth_z()
        cuts.append(
            Pos(0, 0, (mouth + seat) / 2) * Cylinder(SOCKET_ID / 2, (seat - mouth) + 1.0)
        )
        cuts.append(
            Pos(0, 0, (seat - HUB_CAV_H / 2) / 2)
            * Cylinder(9.0, abs(seat + HUB_CAV_H / 2) + 4.0)
        )
        cuts.append(_hub_oring())
    body = _cut(body, cuts)

    # Short rails clear of the six bores, which enter on a circle near the caps.
    rail_y = CORE_Y / 2 + RAIL_CLEAR / 2 + 1.6
    rail_z = sign * (CORE_Z / 2 + 3.0)
    for side in (-1, 1):
        body += Pos(0, side * rail_y, rail_z) * Box(70, 3.2, 6)
    if upper:
        skirt_r = HUB_CAV_R - 0.8
        skirt = Pos(0, 0, -2.0) * (Cylinder(skirt_r, 4) - Cylinder(skirt_r - 2.4, 6))
        body += skirt
    return body


def mast_stub():
    """Visual of the mast. Not a printed part. Inserts 40 mm and continues down."""
    seat = mast_seat_z()
    end = mast_mouth_z() - 90.0
    mid = (seat + end) / 2
    length = seat - end
    outer = Pos(0, 0, mid) * Cylinder(PIPE_OD / 2, length)
    inner = Pos(0, 0, mid) * Cylinder(PIPE_ID / 2, length + 2)
    return outer - inner


def _arrow():
    """One connected arrow in the XY plane, pointing +X, thickness +Z."""
    half = 1.6
    barb = 4.4
    shaft = 11.0
    profile = Polyline(
        (0, -half),
        (shaft, -half),
        (shaft, -barb),
        (ARROW_LENGTH, 0),
        (shaft, barb),
        (shaft, half),
        close=True,
    )
    return extrude(make_face(profile), ARROW_RELIEF)


def marks():
    """North arrow on the up face of the microphone-1 pod, in the pod's frame.

    Same coordinates as pod.stl, so a second filament lands on that face.
    The arrow points horizontally north once the pod is on microphone 1.
    """
    frame = mic_frames()[0]
    cy = _board_center()[1]
    cav_y = BOARD_H + 2 * BOARD_CLEAR
    offset = cy + cav_y / 2 + POD_WALL
    north = Vector(1, 0, 0)
    # Pod local +X is frame.x and local +Z is frame.n. North projected onto
    # the up face (normal +Y) is the arrow's length direction.
    direction = Vector(frame.x.dot(north), 0, frame.n.dot(north)).normalized()
    origin = Vector(0, offset - 0.05, -16) - direction * (ARROW_LENGTH / 2)
    plane = Plane(origin=origin, x_dir=direction, z_dir=Vector(0, 1, 0))
    return plane * _arrow()


def place(part, frame: Frame, distance: float):
    """Move a part built on +Z so its origin lies at frame.n * distance."""
    return frame.plane_at(distance) * part


def placed_arm(frame: Frame):
    # Arm local origin is the spigot tip, which seats at SEAT_R.
    local = arm()
    return place(local, frame, SEAT_R)


def placed_pod(frame: Frame):
    return place(pod(), frame, ACOUSTIC_R)


def placed_window(frame: Frame):
    return place(pod_window(), frame, ACOUSTIC_R)
