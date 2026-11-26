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
# looks back at the same body. The cavity holds the centered v4.6.0 stack.
HUB_CAV_R = 102.0
HUB_R = 110.0
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

# Collar face, local to the pod. Kept inside the floret, clear of the crown.
POD_SHOULDER = -30.0
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

# Satellite, KiCad het68-sat v4.6.0. Origin is a corner of the 50 × 80 board.
# T5848 and the LED ring share (25, 58). RJ45 is on the inner side, toward y=0.
BOARD_W = 50.0
BOARD_H = 80.0
PORT_ON_BOARD = (25.0, 58.0)
SAT_RJ45 = (14.0, 16.0)
LED_RING_R = 12.0
LED_BODY = 5.0
MOUNT_HOLES = ((42.0, 12.0), (8.0, 40.0), (42.0, 66.0), (8.0, 74.0))
BOARD_CLEAR = 3.0  # světlost 56 × 86
POD_WALL = 3.0
PCB_T = 1.6
LIP = 1.6
# Amphenol RJHSE538X body, and the IEC 60603-7 plug that has to pass the bore.
RJ45_H = 13.6
RJ45_PLUG_W = 11.7
RJ45_PLUG_H = 8.0

# Core 160 × 100 and power 140 × 80, both from het68_pcb v4.6.0, centered.
# Power components face down (21700 toward the mast). Core components face
# up (the six RJ45 toward the upper hemisphere). Bare faces look at each other.
CORE_X, CORE_Y = 160.0, 100.0
POWER_X, POWER_Y = 140.0, 80.0
PWR_BOARD_Z = -2.0
CORE_BOARD_Z = 8.0
CELL_H = 23.0  # Keystone 1122 with a 21700 cell, below the power board
# RJ45 on the core, board coordinates, along the y=10 edge. Order is MIC 1..6.
CORE_RJ45 = (
    (14.0, 10.0),
    (38.0, 10.0),
    (62.0, 10.0),
    (86.0, 10.0),
    (110.0, 10.0),
    (134.0, 10.0),
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
    """Corners of the core, the power board, the cell and the six jacks."""
    pts = []
    z0, z1 = CORE_BOARD_Z, CORE_BOARD_Z + PCB_T + RJ45_H
    for x in (-CORE_X / 2, CORE_X / 2):
        for y in (-CORE_Y / 2, CORE_Y / 2):
            pts.append((x, y, z0))
            pts.append((x, y, z1))
    z0, z1 = PWR_BOARD_Z - CELL_H, PWR_BOARD_Z + PCB_T
    for x in (-POWER_X / 2, POWER_X / 2):
        for y in (-POWER_Y / 2, POWER_Y / 2):
            pts.append((x, y, z0))
            pts.append((x, y, z1))
    return pts


def cable_length() -> float:
    """Cat6 between a satellite plug and its core plug. Same cut on all six.

    The path is the plug in the floret, the shared stalk, then the run inside
    the crown to that microphone's jack. All six are cut to the longest one.
    """
    frames = mic_frames()
    lx, ly = board_local(*SAT_RJ45)
    longest = 0.0
    for i, frame in enumerate(frames):
        start = frame.point(ACOUSTIC_R - 3.2, lx, ly)
        plug = frame.point(ACOUSTIC_R - 3.2, lx, ly - 22.0)
        bore = frame.point(ACOUSTIC_R - 28.0)
        mouth = frame.point(HUB_CAV_R + 2.0)
        jx, jy = board_world_xy(*CORE_RJ45[i], CORE_X, CORE_Y)
        jack = Vector(jx, jy, CORE_BOARD_Z + PCB_T)
        # Step outside the stack before crossing the cavity, so the length
        # is a path the cable can actually take.
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
