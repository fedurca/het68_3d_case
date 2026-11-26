"""Dimensions for the het68 384 mm cube-on-vertex case.

Microphone directions are MIC_DIR from het68 doa.c. The acoustic baseline
between opposite faces is the cube edge, 384 mm.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from build123d import Plane, Vector

EDGE_MM = 384.0
ACOUSTIC_R = EDGE_MM / 2.0  # face-centre radius, 192 mm
VERTEX_R = EDGE_MM * (3.0 ** 0.5) / 2.0  # half body diagonal, 332.55 mm

# Unit face normals, USB channel order 1..6. Copied from doa.c.
MIC_DIR = (
    (0.81650, 0.00000, 0.57735),
    (-0.40825, 0.70711, 0.57735),
    (-0.40825, -0.70711, 0.57735),
    (-0.81650, 0.00000, -0.57735),
    (0.40825, -0.70711, -0.57735),
    (0.40825, 0.70711, -0.57735),
)
SPINE_DIR = (0.0, 0.0, -1.0)

# HT DN 32, ČSN EN 1451-1. Printed spigot is 0.3 mm under nominal so it
# enters a real socket. Printed socket is 0.4 mm over nominal so a real
# pipe still enters.
PIPE_OD = 32.0
PIPE_ID = 28.4
SPIGOT_OD = 31.7
SOCKET_ID = 32.4
SOCKET_WALL = 4.5
KEY_WIDTH = 4.0
KEY_HEIGHT = 1.8
KEY_LENGTH = 12.0
GROOVE_WIDTH = 5.2
GROOVE_DEPTH = 2.4
GROOVE_LENGTH = 16.0

# Spherical crown. One outer radius in every direction, so each microphone
# looks back at the same body. The cavity is the smallest sphere that still
# clears the centered core: the 160 × 100 mm corners sit at r = 94.8 mm.
# The wall is 6 mm, which leaves a skin on both sides of the O-ring groove.
HUB_CAV_R = 97.0
HUB_R = 103.0
SPIGOT_LEN = 28.0
# Spigot tip stays outside the stack. The flange is one spigot further out.
SEAT_R = 96.0
MOUTH_R = SEAT_R + SPIGOT_LEN
MAST_SPIGOT = 40.0
MAST_SEAT_Z = -(HUB_CAV_R + 2.0)
# Measurements of reference/stl/spojka-echo.stl. The printable crown is the
# sphere above; these numbers stay so the reference mesh can be placed.
SPOJK_MOUTH = 60.0
SPOJK_BORE_R = 16.60
SPOJK_MOUTH_OD_R = 22.50
SPOJK_MAST_MOUTH = 78.23
# Three Ø12 transducer holes around the stem, kept from the spojka layout.
PIEZO_DIA = 12.0
PIEZO_AXIS_R = 48.0
PIEZO_AZ = (0.0, 120.0, 240.0)
PIEZO_BOSS_R = 11.0
PIEZO_BOSS_LEN = 6.0

# Collar face, local to the pod. Kept inside the head, clear of the crown.
POD_SHOULDER = -30.0
# One sphere on the microphone axis, wrapped around the 52 mm square.
POD_BALL_R = 47.0
POD_BALL_Z = -12.0
POD_CAV_BACK = -24.0
COLLAR_FACE_R = ACOUSTIC_R + POD_SHOULDER
COLLAR_LEN = 14.0
COLLAR_OD = 40.0
# Printed stalk between the crown and the floret. Thicker than the HT pipe
# so the boom reads as a stem. The HT spigot at the crown stays DN 32.
STALK_R = 22.0
FLANGE_OD = 40.0
FLANGE_LEN = 3.0
LUG_WIDTH = 8.0
LUG_RADIAL = 2.4
LUG_AXIAL = 4.0
# Locked lug sits this far back from the collar's outer face.
LUG_FROM_FACE = 6.0
# Bayonet enters 30° off the locked clocking, then twists back.
BAYONET_TWIST_DEG = 30.0

# Satellite het68_pcb v7.4.0. Square 52 × 52 mm, port at the centre.
# Edge.Cuts (0, 0)–(52, 52). T5848 at (26, 26). Eight SK6812 on a circle
# of radius 16 mm. Vertical RJ45 courtyard is centred on (26, 10.4), on
# the ground side of the port. M3 holes are 4.2 mm in from each corner.
BOARD_W = 52.0
BOARD_H = 52.0
PORT_ON_BOARD = (26.0, 26.0)
SAT_RJ45 = (26.0, 10.4)
LED_RING_R = 16.0
LED_BODY = 5.0
MOUNT_HOLES = ((47.8, 4.2), (4.2, 4.2), (47.8, 47.8), (4.2, 47.8))
BOARD_CLEAR = 2.0
POD_WALL = 3.0
PCB_T = 1.6
LIP = 1.6
# Vertical 8P8C housing. The plug that has to pass the bore is IEC 60603-7.
RJ45_H = 17.0
RJ45_PLUG_W = 11.7
RJ45_PLUG_H = 8.0
# Courtyard of het68:RJ45_Vertical_het68, relative to the footprint origin.
RJ45_COURT = (-3.80, -13.33, 12.69, 4.17)

# Core 160 × 100 and power 140 × 80. Outlines are unchanged in het68_pcb v7.4.0.
# Power components face down (21700 toward the mast). Core components face
# up (six vertical RJ45 toward the upper hemisphere). Bare faces look at each other.
CORE_X, CORE_Y = 160.0, 100.0
POWER_X, POWER_Y = 140.0, 80.0
PWR_BOARD_Z = -2.0
CORE_BOARD_Z = 8.0
CELL_H = 23.0  # Keystone 1122 with a 21700 cell, below the power board
# Vertical RJ45 on the core, board coordinates, along y = 7.2. Order is MIC 1..6.
CORE_RJ45 = (
    (14.0, 7.2),
    (38.0, 7.2),
    (62.0, 7.2),
    (86.0, 7.2),
    (110.0, 7.2),
    (134.0, 7.2),
)
# M3 holes, board coordinates. Power holes are a symmetric rectangle.
POWER_HOLES = ((4.0, 4.0), (4.0, 76.0), (136.0, 4.0), (136.0, 76.0))
CORE_HOLES = ((4.95, 70.95), (6.0, 94.0), (154.0, 6.0), (154.0, 94.0))
# Keystone 1122 body on the power board, used to keep the posts off the cell.
CELL_CENTER = (78.0, 62.0)
CELL_BODY = (91.2, 23.1)
RAIL_CLEAR = 0.8
SCREW_D = 3.4
ORING_CORD = 2.5

# North arrow, printed either in the body colour or as a second filament.
ARROW_LENGTH = 18.0
ARROW_RELIEF = 0.8


def board_local(px: float, py: float) -> tuple[float, float]:
    """Board point to pod coordinates. +Y is away from the RJ45 edge."""
    return (px - PORT_ON_BOARD[0], py - PORT_ON_BOARD[1])


@dataclass(frozen=True)
class Frame:
    """Right-handed frame. +Z is the face normal (outward), −Y is the key side.

    The key side is world-down projected onto the face, so the RJ45 edge of
    the satellite points at the ground. On the vertical spine the reference
    is north (+X), because down is parallel to the tube.
    """

    n: Vector
    x: Vector
    y: Vector

    @staticmethod
    def from_direction(direction: tuple[float, float, float]) -> "Frame":
        n = Vector(*direction).normalized()
        ref = Vector(0, 0, -1)
        if abs(n.dot(ref)) > 0.95:
            ref = Vector(1, 0, 0)
        toward = (ref - n * n.dot(ref)).normalized()
        y = -toward
        x = y.cross(n).normalized()
        y = n.cross(x).normalized()
        return Frame(n, x, y)

    def plane_at(self, distance: float) -> Plane:
        return Plane(origin=self.n * distance, x_dir=self.x, z_dir=self.n)

    def point(self, along: float, across_x: float = 0.0, across_y: float = 0.0) -> Vector:
        return self.n * along + self.x * across_x + self.y * across_y


def mic_frames() -> list[Frame]:
    return [Frame.from_direction(d) for d in MIC_DIR]


def opposite_distance(i: int) -> float:
    a = Vector(*MIC_DIR[i])
    b = Vector(*MIC_DIR[(i + 3) % 6])
    return (a - b).length * ACOUSTIC_R


def shell_radius() -> float:
    """Outer crown radius. A sphere, so this is the same in every direction."""
    return HUB_R


def board_world_xy(px: float, py: float, width: float, height: float) -> tuple[float, float]:
    """Board point when that board is centered on the origin."""
    return (px - width / 2.0, py - height / 2.0)


def stack_points():
    """Corners of the core copper, the six vertical jacks, and the power stack.

    The power rectangle is extended down over the cell, which is smaller than
    the board, so the check stays conservative without inflating the core up
    to the top of the jacks.
    """
    pts = []
    for x in (-CORE_X / 2, CORE_X / 2):
        for y in (-CORE_Y / 2, CORE_Y / 2):
            pts.append((x, y, CORE_BOARD_Z))
            pts.append((x, y, CORE_BOARD_Z + PCB_T))
    x0, y0, x1, y1 = RJ45_COURT
    z_jack = CORE_BOARD_Z + PCB_T + RJ45_H
    for px, py in CORE_RJ45:
        ox, oy = board_world_xy(px, py, CORE_X, CORE_Y)
        for dx in (x0, x1):
            for dy in (y0, y1):
                pts.append((ox + dx, oy + dy, z_jack))
    z0, z1 = PWR_BOARD_Z - CELL_H, PWR_BOARD_Z + PCB_T
    for x in (-POWER_X / 2, POWER_X / 2):
        for y in (-POWER_Y / 2, POWER_Y / 2):
            pts.append((x, y, z0))
            pts.append((x, y, z1))
    return pts


def cable_length() -> float:
    """Cat6 between a satellite plug and its core plug. Same cut on all six.

    The plug leaves the satellite jack along the stalk axis, joins the bore,
    then crosses the crown to that microphone's jack.
    """
    frames = mic_frames()
    lx, ly = board_local(*SAT_RJ45)
    longest = 0.0
    for i, frame in enumerate(frames):
        start = frame.point(ACOUSTIC_R - 2 * PCB_T, lx, ly)
        plug = frame.point(ACOUSTIC_R - 30.0, lx, ly)
        bore = frame.point(ACOUSTIC_R - 40.0)
        mouth = frame.point(HUB_CAV_R + 2.0)
        jx, jy = board_world_xy(*CORE_RJ45[i], CORE_X, CORE_Y)
        jack = Vector(jx, jy, CORE_BOARD_Z + PCB_T + RJ45_H)
        side = Vector(mouth.X, mouth.Y, jack.Z)
        run = 0.0
        prev = start
        for point in (plug, bore, mouth, side, jack):
            run += (point - prev).length
            prev = point
        longest = max(longest, run)
    # Two plug bodies and a coil of spare inside the crown.
    return float(math.ceil((longest + 40.0) / 10.0) * 10.0)


def mast_seat_z() -> float:
    """Pipe stop inside the lower crown. The bore does not enter the cavity."""
    return MAST_SEAT_Z


def mast_mouth_z() -> float:
    return MAST_SEAT_Z - MAST_SPIGOT
