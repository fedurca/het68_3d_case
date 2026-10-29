"""Printable parts for the 384 mm het68 array.

The crown is a sealed sphere, so every direction sees the same body.
Six identical stalks end in florets. The mast is the stem.
"""

from __future__ import annotations

from build123d import (
    Align,
    Box,
    Cone,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    Rot,
    Sphere,
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
    FLANGE_LEN,
    FLANGE_OD,
    GROOVE_DEPTH,
    GROOVE_WIDTH,
    HUB_CAV_R,
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
    MAST_SEAT_Z,
    MOUTH_R,
    ORING_CORD,
    POD_SHOULDER,
    PCB_T,
    PIPE_ID,
    PIPE_OD,
    POD_WALL,
    SCREW_D,
    SEAT_R,
    SOCKET_ID,
    SOCKET_WALL,
    SPIGOT_LEN,
    SPIGOT_OD,
    STALK_R,
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


def _root(frame: Frame, z0: float, z1: float, r0: float, r1: float):
    """Taper along frame.n. Wider at z0, where the stalk leaves the crown."""
    body = Cone(r0, r1, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))
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
    # Thick stem stops before the collar, so the collar can pass the floret's bore.
    stalk_end = collar0 - 6.0
    parts = [
        _tube(frame, 0, SPIGOT_LEN, SPIGOT_OD / 2, bore),
        _tube(frame, SPIGOT_LEN, SPIGOT_LEN + FLANGE_LEN, FLANGE_OD / 2, bore),
        _tube(frame, SPIGOT_LEN + FLANGE_LEN, stalk_end, STALK_R, bore),
        _tube(frame, stalk_end, collar0, COLLAR_OD / 2, bore),
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
    # Bell slides over the crown socket so rain runs off the joint.
    boss_r = SOCKET_ID / 2 + SOCKET_WALL
    # Short hood over the socket mouth. It stays clear of the root bulb.
    parts.append(_tube(frame, SPIGOT_LEN - 6.0, SPIGOT_LEN + 0.3, boss_r + 2.8, boss_r + 0.5))
    parts.append(_tube(frame, SPIGOT_LEN - 0.4, SPIGOT_LEN + FLANGE_LEN, boss_r + 2.8, bore))
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
    cx, cy = _board_center()
    cav_x = BOARD_W + 2 * BOARD_CLEAR
    cav_y = BOARD_H + 2 * BOARD_CLEAR
    shoulder = POD_SHOULDER
    mouth = shoulder - COLLAR_LEN - 2.0
    cav_front = -PCB_T
    cav_back = -32.0

    # Three overlapping buds along the board. The port bud is the one at +Y.
    lobes = [
        Pos(0, cy - 24.0, -16) * Sphere(42),
        Pos(0, cy, -16) * Sphere(40),
        Pos(0, cy + 18.0, -14) * Sphere(46),
    ]
    bud = _fuse(lobes)
    bud -= Pos(0, 0, 60) * Box(260, 320, 120)
    # Hood over the thick stem. Its bore is wider than the collar, so the
    # collar slides through and seats in the tighter bore beyond.
    hood = Pos(0, 0, -56) * Cylinder(STALK_R + 5.0, 14)
    shell = bud + hood
    void = Pos(cx, cy, (cav_back + cav_front) / 2) * Box(
        cav_x, cav_y, (cav_front - cav_back) + 0.05
    )
    mic = Cylinder(3.2, 8, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    led_outer = Cylinder(LED_RING_R + 4.2, 6)
    led_inner = Cylinder(LED_RING_R - 4.0, 8)
    led = led_outer - led_inner
    # Shallow seat for the cover. The centre web around the microphone stays.
    lap = Pos(0, 0, -0.4) * Cylinder(LED_RING_R + 6.4, 1.0)
    lap -= Pos(0, 0, -0.4) * Cylinder(LED_RING_R - 3.8, 2.2)

    # Hood bore first (wide), then the collar bore. The collar never has to
    # pass a hole smaller than itself.
    hood_bore = Pos(0, 0, (-63 + mouth) / 2) * Cylinder(
        STALK_R + 0.6, mouth + 63 + 0.4
    )
    collar_bore = Pos(0, 0, (mouth + shoulder) / 2) * Cylinder(
        COLLAR_OD / 2 + 0.45, abs(shoulder - mouth) + 0.2
    )
    # Shoulder is the blind end of collar_bore at z=shoulder. Extend it a
    # hair past the shoulder so the boolean face is clean, but not into the
    # board cavity (cavity ends near z=-1.6, shoulder is -32).
    cuts = [void, mic, led, lap, hood_bore, collar_bore]
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
        post = Pos(lx, ly, -8.0) * Cylinder(
            4.2, 14, align=(Align.CENTER, Align.CENTER, Align.CENTER)
        )
        hole = Pos(lx, ly, -8.0) * Cylinder(
            1.6, 16, align=(Align.CENTER, Align.CENTER, Align.CENTER)
        )
        posts.append(post - hole)
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


def _hub_lugs(sign: float):
    """Screw pads in the cavity, clear of the 160 × 100 stack."""
    pads = []
    for x, y in ((86.0, 0.0), (-86.0, 0.0), (0.0, 66.0), (0.0, -66.0)):
        pad = Pos(x, y, sign * 4.5) * Cylinder(5.0, 9)
        hole = Pos(x, y, sign * 4.5) * Cylinder(SCREW_D / 2, 12)
        pads.append(pad - hole)
    return pads


def _hub_oring():
    """Groove in the lower equator face. The outside of the crown stays a sphere."""
    radius = (HUB_R + HUB_CAV_R) / 2
    half_w = ORING_CORD * 0.7
    depth = 1.6
    z = -depth / 2 + 0.2
    outer = Pos(0, 0, z) * Cylinder(radius + half_w, depth + 0.4)
    inner = Pos(0, 0, z) * Cylinder(radius - half_w, depth + 1.4)
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


def _half_ball(upper: bool):
    ball = Sphere(HUB_R)
    # Box covers the unwanted hemisphere and stops on the equator.
    cutter = Pos(0, 0, (-1 if upper else 1) * HUB_R) * Box(HUB_R * 4, HUB_R * 4, HUB_R * 2)
    return ball - cutter


def _hub_half(upper: bool):
    """Half of the spherical crown. Three stalks each; the stem is on the lower half."""
    sign = 1.0 if upper else -1.0
    frames = mic_frames()[:3] if upper else mic_frames()[3:]
    r_boss = SOCKET_ID / 2 + SOCKET_WALL
    # Flare where the stalk leaves the sphere, then a straight socket the bell covers.
    roots = [_root(frame, HUB_R - 8.0, HUB_R + 6.0, 34.0, r_boss) for frame in frames]
    bosses = [_solid_cyl(frame, HUB_R + 2.0, MOUTH_R, r_boss) for frame in frames]
    parts = [_half_ball(upper), *roots, *bosses]
    if not upper:
        mouth = mast_mouth_z()
        # Stem: wide root, straight socket, drip ring at the open end.
        parts.append(Pos(0, 0, -(HUB_R + 8.0)) * Cone(r_boss, 34.0, 16.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))
        parts.append(
            Pos(0, 0, (mouth + (-HUB_R - 4)) / 2) * Cylinder(r_boss, (-HUB_R - 4) - mouth)
        )
        parts.append(Pos(0, 0, mouth + 3) * Cylinder(r_boss + 3.5, 5))
    body = _fuse(parts)

    cavity = Sphere(HUB_CAV_R + (0.0 if upper else 0.4))
    bores = [
        _solid_cyl(frame, SEAT_R - 6.0, MOUTH_R + 1.0, SOCKET_ID / 2) for frame in frames
    ]
    cuts = [cavity, *bores, *_socket_grooves(frames)]
    if not upper:
        mouth = mast_mouth_z()
        seat = mast_seat_z()
        cuts.append(Pos(0, 0, (mouth + seat) / 2) * Cylinder(SOCKET_ID / 2, seat - mouth + 0.6))
        cuts.append(_hub_oring())
    body = _cut(body, cuts)
    body += _fuse(_hub_lugs(sign))
    if upper:
        # Tongue nests into the lower cavity. The outer surface stays flush.
        tongue_r = HUB_CAV_R - 0.7
        tongue = Pos(0, 0, -1.6) * (Cylinder(tongue_r, 3.2) - Cylinder(tongue_r - 2.6, 5))
        body += tongue
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
    north = Vector(1, 0, 0)
    # Pod local +X is frame.x and local +Z is frame.n. North projected onto
    # the up side of the port bud is the arrow's length direction.
    direction = Vector(frame.x.dot(north), 0, frame.n.dot(north)).normalized()
    origin = Vector(0, cy + 18.0 + 46.0, -14) - direction * (ARROW_LENGTH / 2)
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
