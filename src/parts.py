"""Printable parts for the 384 mm het68 array.

The hub is only a cable junction. Core and the power board live in the box
under the lower vertex, where no microphone looks. Arms are HT DN 32 tubes
with one clocking rib at the hub and one bayonet lug at the pod.
"""

from __future__ import annotations

from build123d import (
    Align,
    Box,
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
    BOSS_LEN,
    BOX_CAV_Z0,
    BOX_CAV_Z1,
    BOX_FLANGE,
    BOX_IN_X,
    BOX_IN_Y,
    BOX_IN_Z,
    BOX_WALL,
    CAVITY_R,
    COLLAR_FACE_R,
    COLLAR_LEN,
    COLLAR_OD,
    CORE_Y,
    FLANGE_LEN,
    FLANGE_OD,
    GROOVE_DEPTH,
    GROOVE_LENGTH,
    GROOVE_WIDTH,
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


def hub():
    """Six microphone sockets plus the downward spine socket."""
    frames = mic_frames() + [Frame.from_direction((0.0, 0.0, -1.0))]
    r_out = SOCKET_ID / 2 + SOCKET_WALL
    bosses = [
        _solid_cyl(frame, CAVITY_R - 2, MOUTH_R, r_out) for frame in frames
    ]
    body = _fuse([Sphere(HUB_R), *bosses])
    bores = [
        _solid_cyl(frame, CAVITY_R - 4, MOUTH_R + 1, SOCKET_ID / 2) for frame in frames
    ]
    grooves = []
    for frame in frames:
        # Side relief at the inner end of the bore. A round pipe still seats.
        # Our rib fills the relief and sets the rotation.
        # Full-length relief so the spigot rib can slide in from the mouth.
        # A plain round pipe still seats; the rib only clocks the printed arm.
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
    return _cut(body, [Sphere(CAVITY_R), *bores, *grooves])


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


def _box_outer(z0: float, z1: float, wall: float):
    outer = Box(BOX_IN_X + 2 * wall, BOX_IN_Y + 2 * wall, z1 - z0)
    outer = Pos(0, 0, (z0 + z1) / 2) * outer
    return outer


def _flange(z_mid: float, thickness: float):
    width_x = BOX_IN_X + 2 * BOX_WALL + 2 * BOX_FLANGE
    width_y = BOX_IN_Y + 2 * BOX_WALL + 2 * BOX_FLANGE
    plate = Pos(0, 0, z_mid) * Box(width_x, width_y, thickness)
    hole = Pos(0, 0, z_mid) * Box(BOX_IN_X - 1, BOX_IN_Y - 1, thickness + 2)
    return plate - hole


def _screw_holes(z0: float, z1: float):
    width_x = BOX_IN_X + 2 * BOX_WALL + 2 * BOX_FLANGE
    width_y = BOX_IN_Y + 2 * BOX_WALL + 2 * BOX_FLANGE
    inset = 6.0
    xs = (-width_x / 2 + inset, width_x / 2 - inset)
    ys = (-width_y / 2 + inset, width_y / 2 - inset)
    holes = []
    for x in xs:
        for y in ys:
            holes.append(
                Pos(x, y, (z0 + z1) / 2)
                * Cylinder(SCREW_D / 2, (z1 - z0) + 4)
            )
    return holes


def _oring_groove(z_face: float):
    """Groove opening through the flange face. Depth is 1.7 mm for a 2.5 mm cord."""
    depth = 1.7
    height = depth + 0.8
    z = z_face - depth / 2 + 0.4
    width_x = BOX_IN_X + 2 * BOX_WALL + BOX_FLANGE
    width_y = BOX_IN_Y + 2 * BOX_WALL + BOX_FLANGE
    outer = Pos(0, 0, z) * Box(width_x, width_y, height)
    inner = Pos(0, 0, z) * Box(
        width_x - 2 * ORING_CORD * 1.5,
        width_y - 2 * ORING_CORD * 1.5,
        height + 1,
    )
    return outer - inner


def electronics_box():
    """Lower half. Flange faces up. The mast socket hangs under the floor."""
    z_join = (BOX_CAV_Z0 + BOX_CAV_Z1) / 2
    z_bot = BOX_CAV_Z0 - BOX_WALL
    shell = _box_outer(z_bot, z_join, BOX_WALL)
    cavity = Pos(0, 0, (BOX_CAV_Z0 + z_join) / 2 + 1) * Box(
        BOX_IN_X, BOX_IN_Y, (z_join - BOX_CAV_Z0) + 4
    )
    flange = _flange(z_join - 2.5, 5)
    body = _fuse([shell, flange]) - cavity

    mouth = z_bot - BOSS_LEN
    seat = mouth + SPIGOT_LEN
    boss = Pos(0, 0, (z_bot + mouth) / 2) * Cylinder(
        SOCKET_ID / 2 + SOCKET_WALL, z_bot - mouth
    )
    bore = Pos(0, 0, (mouth + seat) / 2) * Cylinder(SOCKET_ID / 2, seat - mouth + 0.4)
    # North side of the bore, so a rib on +X clocks the mast the same way as the spine.
    groove = Pos(
        SOCKET_ID / 2 + GROOVE_DEPTH / 2 - 0.2,
        0,
        seat - GROOVE_LENGTH / 2,
    ) * Box(GROOVE_DEPTH + 1.0, GROOVE_WIDTH, GROOVE_LENGTH)
    body = _fuse([body, boss])
    # Pipe stops on the seat. A smaller hole continues into the cavity for the cables.
    cable = Pos(0, 0, (seat + BOX_CAV_Z0) / 2) * Cylinder(9, (BOX_CAV_Z0 - seat) + 4)
    body = _cut(
        body,
        [bore, cable, groove, _oring_groove(z_join), *_screw_holes(z_join - 6, z_join + 1)],
    )

    gap = CORE_Y + RAIL_CLEAR
    rail_z = BOX_CAV_Z0 + 4
    for sign in (-1, 1):
        body += Pos(0, sign * (gap / 2 + 1.6), rail_z) * Box(BOX_IN_X - 4, 3.2, 8)
    return body


def electronics_lid():
    """Upper half. Flange faces down onto the box. Spine socket points at the hub."""
    z_join = (BOX_CAV_Z0 + BOX_CAV_Z1) / 2
    z_top = BOX_CAV_Z1 + BOX_WALL
    shell = _box_outer(z_join, z_top, BOX_WALL)
    cavity = Pos(0, 0, (z_join + BOX_CAV_Z1) / 2 - 1) * Box(
        BOX_IN_X, BOX_IN_Y, (BOX_CAV_Z1 - z_join) + 4
    )
    flange = _flange(z_join + 2.5, 5)
    skirt = Pos(0, 0, z_join - 2) * Box(BOX_IN_X - 2.0, BOX_IN_Y - 2.0, 4)
    skirt_hole = Pos(0, 0, z_join - 2) * Box(BOX_IN_X - 8, BOX_IN_Y - 8, 6)
    body = _fuse([shell, flange, skirt - skirt_hole]) - cavity

    mouth = z_top + BOSS_LEN
    seat = mouth - SPIGOT_LEN
    boss = Pos(0, 0, (z_top + mouth) / 2) * Cylinder(
        SOCKET_ID / 2 + SOCKET_WALL, mouth - z_top
    )
    bore = Pos(0, 0, (mouth + seat) / 2) * Cylinder(SOCKET_ID / 2, mouth - seat + 0.4)
    groove = Pos(
        SOCKET_ID / 2 + GROOVE_DEPTH / 2 - 0.2,
        0,
        seat + GROOVE_LENGTH / 2,
    ) * Box(GROOVE_DEPTH + 1.0, GROOVE_WIDTH, GROOVE_LENGTH)
    body = _fuse([body, boss])
    cable = Pos(0, 0, (seat + BOX_CAV_Z1) / 2) * Cylinder(9, (seat - BOX_CAV_Z1) + 4)
    body = _cut(body, [bore, cable, groove, *_screw_holes(z_join - 1, z_join + 6)])
    return body


def spine_pipe():
    """Visual of the cut HT pipe. Not a printed part; shown in the renders."""
    hub_z, lid_z = _spine_ends()
    length = abs(lid_z - hub_z)
    mid = (hub_z + lid_z) / 2
    outer = Pos(0, 0, mid) * Cylinder(PIPE_OD / 2, length)
    inner = Pos(0, 0, mid) * Cylinder(PIPE_ID / 2, length + 2)
    return outer - inner


def _spine_ends() -> tuple[float, float]:
    from params import spine_seats

    return spine_seats()


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
