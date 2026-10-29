"""Dimensions for the het68 384 mm cube-on-vertex case.

Microphone directions are MIC_DIR from het68 doa.c. The acoustic baseline
between opposite faces is the cube edge, 384 mm.
"""

from __future__ import annotations

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

# Spherical crown. One radius in every direction, so the body each
# microphone looks back at is the same shape. The stack sits at the origin.
HUB_CAV_R = 102.0
HUB_R = 110.0
# Printed arm seats outside the board. The real mast pipe uses a deeper socket.
SEAT_R = 96.0
SPIGOT_LEN = 28.0
MOUTH_R = SEAT_R + SPIGOT_LEN
MAST_SPIGOT = 40.0
# Stop just outside the cavity so the stem socket stays a blind hole.
MAST_SEAT_Z = -(HUB_CAV_R + 2.0)

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

# Satellite board, KiCad het68-sat v4.5.0, millimetres, origin at a corner.
BOARD_W = 50.0
BOARD_H = 80.0
PORT_ON_BOARD = (25.0, 58.708)  # T5848 acoustic port
LED_RING_R = 12.0
LED_BODY = 5.0
MOUNT_HOLES = ((42.0, 12.0), (8.0, 40.0), (42.0, 66.0), (8.0, 74.0))
BOARD_CLEAR = 3.0  # světlost 56 × 86
POD_WALL = 3.0
PCB_T = 1.6
LIP = 1.6

# Electronics stack envelope from the v4.5.0 outlines plus the 21700 holder.
# The stack is centered on the origin. The round cavity is wider than the
# board so the six angled bores open into it without clipping the wall.
CORE_X, CORE_Y, CORE_Z = 160.0, 100.0, 54.0
POWER_X, POWER_Y = 140.0, 80.0
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


def cable_length() -> float:
    """Straight run from a T5848 plane to the crown cavity. Same everywhere."""
    return ACOUSTIC_R - HUB_CAV_R


def mast_seat_z() -> float:
    """Pipe stop inside the lower crown. Blind: the bore does not enter the cavity."""
    return MAST_SEAT_Z


def mast_mouth_z() -> float:
    return MAST_SEAT_Z - MAST_SPIGOT
