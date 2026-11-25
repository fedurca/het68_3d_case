"""Build every printable part and write STL, STEP, renders and the pipe cut."""

from __future__ import annotations

from pathlib import Path

from build123d import export_step, export_stl

from check import check_baselines, check_meshes, check_solids
from hub_mesh import render_arrays, write_hub
from params import ACOUSTIC_R, MAST_SPIGOT, SEAT_R, cable_length, mic_frames
from parts import (
    arm,
    marks,
    mast_stub,
    place,
    pod,
    pod_window,
)
from render import render_mesh, render_part, render_views

GREEN = (0.36, 0.55, 0.32)
GREEN_DARK = (0.28, 0.46, 0.27)
WINDOW = (0.78, 0.88, 0.74)
ARROW = (0.93, 0.93, 0.88)
PIPE = (0.62, 0.64, 0.66)

ROOT = Path(__file__).resolve().parents[1]


def _export(part, name: str, stl_dir: Path, step_dir: Path):
    export_stl(part, str(stl_dir / f"{name}.stl"), tolerance=0.12, angular_tolerance=0.25)
    export_step(part, str(step_dir / f"{name}.step"))


def main():
    check_baselines()
    stl_dir = ROOT / "export" / "stl"
    step_dir = ROOT / "export" / "step"
    img_dir = ROOT / "export" / "img"
    for folder in (stl_dir, step_dir, img_dir):
        folder.mkdir(parents=True, exist_ok=True)

    for stale in (
        "hub_lower.stl",
        "hub_upper.stl",
        "hub_lower.step",
        "hub_upper.step",
        "hub_lower.png",
        "hub_upper.png",
    ):
        for folder in (stl_dir, step_dir, img_dir):
            (folder / stale).unlink(missing_ok=True)

    print("placing spojka")
    write_hub(stl_dir / "hub.stl")
    hub_verts, hub_tris = render_arrays()
    print("rendering spojka")
    render_mesh(hub_verts, hub_tris, GREEN_DARK, img_dir / "hub.png")

    print("building arm")
    arm_part = arm()
    print("building pod")
    pod_part = pod()
    print("building window")
    window_part = pod_window()
    print("building mark")
    mark_part = marks()
    check_solids(arm_part, pod_part, window_part)

    singles = {
        "arm": arm_part,
        "pod": pod_part,
        "pod_window": window_part,
        "marks": mark_part,
    }
    for name, part in singles.items():
        print("export", name)
        _export(part, name, stl_dir, step_dir)
        render_part(part, WINDOW if name == "pod_window" else ARROW if name == "marks" else GREEN, img_dir / f"{name}.png")

    frames = mic_frames()
    assembly = [
        (mast_stub(), PIPE),
        (place(mark_part, frames[0], ACOUSTIC_R), ARROW),
    ]
    for frame in frames:
        assembly.append((place(arm_part, frame, SEAT_R), GREEN))
        assembly.append((place(pod_part, frame, ACOUSTIC_R), GREEN))
        assembly.append((place(window_part, frame, ACOUSTIC_R), WINDOW))
    hub_mesh = (hub_verts, hub_tris, GREEN_DARK)

    views = {
        "iso": ((1.0, -0.85, 0.55), (0.0, 0.0, 1.0)),
        "side": ((0.0, -1.0, 0.15), (0.0, 0.0, 1.0)),
        "top": ((0.15, -0.05, 1.0), (0.0, 1.0, 0.0)),
        "bottom": ((0.12, -0.08, -1.0), (0.0, 1.0, 0.0)),
    }
    print("rendering assembly")
    render_views(assembly, img_dir, "assembly", views, extra_meshes=(hub_mesh,))

    (ROOT / "export" / "CUT_LENGTHS.txt").write_text(
        "\n".join(
            [
                "Stožár je skladová trubka HT DN 32, není to tištěný díl.",
                f"Do svislého hrdla spojky se zasouvá {MAST_SPIGOT:.0f} mm.",
                f"Od každého T5848 do středu spojky je to {cable_length():.1f} mm, ve všech směrech stejně.",
                "Průchod kabelu je provrtané hrdlo spojky.",
                "Šest tištěných stopek je stejný díl.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    check_meshes(stl_dir)
    print("done")


if __name__ == "__main__":
    main()
