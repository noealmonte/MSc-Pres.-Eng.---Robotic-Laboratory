"""
MPE Control & Automation — Session 2: Forward Kinematics of the Mecademic Meca500.

Provides both symbolic (SymPy) and numerical (NumPy) forward kinematics using:
1. Simple frame placement (Session 2 Figure 2.2 + Mecademic FRF alignment R_y(pi/2))
2. Craig Denavit-Hartenberg parameters (Robotics Lecture 3, Slide 45)

Orientation uses Mecademic's mobile (intrinsic) XYZ Euler angle convention (alpha, beta, gamma),
equivalent to R = Rx(alpha) @ Ry(beta) @ Rz(gamma).
"""

from __future__ import annotations

import numpy as np
import sympy as sp

# Default Meca500 geometric dimensions [mm] (User Manual Fig. 9 & Lecture 3 Slide 45)
MECA500_PARAMS: dict[str, float] = {
    "l_0": 135.0,
    "l_2": 135.0,
    "l_3": 38.0,
    "l_4": 120.0,
    "l_6": 70.0,
}

# Symbolic variables
theta_1, theta_2, theta_3, theta_4, theta_5, theta_6 = sp.symbols(
    "theta_1 theta_2 theta_3 theta_4 theta_5 theta_6"
)
l_0, l_2, l_3, l_4, l_6 = sp.symbols("l_0 l_2 l_3 l_4 l_6", positive=True)

JOINT_SYMBOLS = (theta_1, theta_2, theta_3, theta_4, theta_5, theta_6)
LENGTH_SYMBOLS = (l_0, l_2, l_3, l_4, l_6)


def Dx(d: sp.Expr | float) -> sp.Matrix:
    """Pure translation along X by distance d."""
    return sp.Matrix([[1, 0, 0, d], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


def Dy(d: sp.Expr | float) -> sp.Matrix:
    """Pure translation along Y by distance d."""
    return sp.Matrix([[1, 0, 0, 0], [0, 1, 0, d], [0, 0, 1, 0], [0, 0, 0, 1]])


def Dz(d: sp.Expr | float) -> sp.Matrix:
    """Pure translation along Z by distance d."""
    return sp.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, d], [0, 0, 0, 1]])


def Rx(angle: sp.Expr | float) -> sp.Matrix:
    """Pure rotation about X by angle [rad]."""
    c, s = sp.cos(angle), sp.sin(angle)
    return sp.Matrix([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])


def Ry(angle: sp.Expr | float) -> sp.Matrix:
    """Pure rotation about Y by angle [rad]."""
    c, s = sp.cos(angle), sp.sin(angle)
    return sp.Matrix([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])


def Rz(angle: sp.Expr | float) -> sp.Matrix:
    """Pure rotation about Z by angle [rad]."""
    c, s = sp.cos(angle), sp.sin(angle)
    return sp.Matrix([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


def dh_craig(
    alpha_prev: sp.Expr | float,
    a_prev: sp.Expr | float,
    d_i: sp.Expr | float,
    theta_i: sp.Expr | float,
) -> sp.Matrix:
    """Modified (Craig) Denavit-Hartenberg link transformation matrix."""
    return Dx(a_prev) * Rx(alpha_prev) * Dz(d_i) * Rz(theta_i)


def build_symbolic_fk_simple(
    align_to_frf: bool = True,
) -> tuple[dict[str, sp.Matrix], sp.Matrix]:
    """
    Build symbolic forward kinematics using the simple frame placement (Session 2 Fig. 2.2).

    At zero joint angles, all frames {B}, {0}..{6}, {T_fig} share (+X forward, +Y left, +Z up).
    When ``align_to_frf=True``, appends ``Ry(pi/2)`` so the final frame matches Mecademic's
    Flange Reference Frame (FRF: +Z outward along joint 6, +Y parallel to +Y_BRF, +X down).
    """
    transforms: dict[str, sp.Matrix] = {
        "T_B_0": Dz(l_0),
        "T_0_1": Rz(theta_1),
        "T_1_2": Ry(theta_2),
        "T_2_3": Dz(l_2) * Ry(theta_3),
        "T_3_4": Dz(l_3) * Dx(l_4) * Rx(theta_4),
        "T_4_5": Ry(theta_5),
        "T_5_6": Rx(theta_6),
        "T_6_T": Dx(l_6),
    }

    T_total = sp.eye(4)
    for mat in transforms.values():
        T_total = T_total * mat

    if align_to_frf:
        transforms["T_T_FRF"] = Ry(sp.pi / 2)
        T_total = T_total * transforms["T_T_FRF"]

    return transforms, T_total


def build_symbolic_fk_dh(
    align_to_frf: bool = True,
) -> tuple[list[sp.Matrix], sp.Matrix]:
    """
    Build symbolic forward kinematics using Craig DH parameters (Lecture 3, Slide 45).

    Appends Dz(l_6) to reach the flange and, when ``align_to_frf=True``, Rz(pi) so
    the flange frame matches Mecademic's FRF (+X down, +Y left, +Z outward).
    """
    dh_table = [
        (0, 0, l_0, theta_1),
        (-sp.pi / 2, 0, 0, theta_2 - sp.pi / 2),
        (0, l_2, 0, theta_3),
        (-sp.pi / 2, l_3, l_4, theta_4),
        (sp.pi / 2, 0, 0, theta_5),
        (-sp.pi / 2, 0, 0, theta_6),
    ]
    links = [dh_craig(*row) for row in dh_table]

    T_total = sp.eye(4)
    for A in links:
        T_total = T_total * A

    T_total = T_total * Dz(l_6)
    if align_to_frf:
        T_total = T_total * Rz(sp.pi)

    return links, T_total


def build_trf_matrix(
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    alpha_deg: float = 0.0,
    beta_deg: float = 0.0,
    gamma_deg: float = 0.0,
) -> np.ndarray:
    """
    Build 4x4 numeric transformation matrix ^FRF_TRF T from SetTrf(x, y, z, alpha, beta, gamma).
    Uses Mecademic's mobile (intrinsic) XYZ Euler angle convention.
    """
    a, b, g = np.deg2rad([alpha_deg, beta_deg, gamma_deg])
    ca, sa = np.cos(a), np.sin(a)
    cb, sb = np.cos(b), np.sin(b)
    cg, sg = np.cos(g), np.sin(g)

    Rx_n = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]], dtype=float)
    Ry_n = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]], dtype=float)
    Rz_n = np.array([[cg, -sg, 0], [sg, cg, 0], [0, 0, 1]], dtype=float)

    T = np.eye(4, dtype=float)
    T[:3, :3] = Rx_n @ Ry_n @ Rz_n
    T[:3, 3] = [x, y, z]
    return T


def rot_to_mecademic_euler(R: np.ndarray, tol: float = 1e-9) -> np.ndarray:
    """
    Extract mobile (intrinsic) XYZ Euler angles [alpha, beta, gamma] in degrees
    from a 3x3 rotation matrix R = Rx(alpha) @ Ry(beta) @ Rz(gamma).

    Matches Mecademic Meca500 controller output ranges:
      -180 <= alpha <= 180, -90 <= beta <= 90, -180 <= gamma <= 180
      and alpha = 0 when |beta| == 90 deg (gimbal lock).
    """
    r13 = float(np.clip(R[0, 2], -1.0, 1.0))
    beta = np.arcsin(r13)

    if np.abs(np.cos(beta)) > tol:
        alpha = np.arctan2(-R[1, 2], R[2, 2])
        gamma = np.arctan2(-R[0, 1], R[0, 0])
    else:
        alpha = 0.0
        gamma = np.arctan2(R[1, 0], R[1, 1])

    angles_deg = np.rad2deg([alpha, beta, gamma])
    # Clean -0.0 and -180.0 (prefer +180.0 for branch cut consistency)
    angles_deg = np.where(np.isclose(angles_deg, 0.0, atol=1e-9), 0.0, angles_deg)
    angles_deg = np.where(np.isclose(angles_deg, -180.0, atol=1e-9), 180.0, angles_deg)
    return angles_deg


class Meca500Kinematics:
    """Numerical evaluator compiled from the SymPy forward kinematics model."""

    def __init__(
        self,
        params: dict[str, float] | None = None,
        method: str = "simple",
        align_to_frf: bool = True,
    ) -> None:
        self.params = dict(MECA500_PARAMS if params is None else params)
        self.method = method
        self.align_to_frf = align_to_frf

        if method == "simple":
            _, T_sym = build_symbolic_fk_simple(align_to_frf=align_to_frf)
        elif method == "dh":
            _, T_sym = build_symbolic_fk_dh(align_to_frf=align_to_frf)
        else:
            raise ValueError(f"Unknown method '{method}'. Expected 'simple' or 'dh'.")

        self.T_sym = T_sym
        self._fk_num = sp.lambdify(
            (*JOINT_SYMBOLS, *LENGTH_SYMBOLS),
            T_sym,
            modules="numpy",
        )

    def forward_transform(
        self,
        joints_deg: list[float] | np.ndarray,
        T_flange_tcp: np.ndarray | None = None,
    ) -> np.ndarray:
        """Compute 4x4 homogeneous transform ^B_TCP T for joint angles in degrees."""
        if len(joints_deg) != 6:
            raise ValueError(f"Expected 6 joint angles, got {len(joints_deg)}.")
        q_rad = np.deg2rad(joints_deg)
        length_vals = [self.params[k] for k in ("l_0", "l_2", "l_3", "l_4", "l_6")]
        T = np.array(self._fk_num(*q_rad, *length_vals), dtype=float)
        if T_flange_tcp is not None:
            T = T @ T_flange_tcp
        return T

    def forward_pose(
        self,
        joints_deg: list[float] | np.ndarray,
        T_flange_tcp: np.ndarray | None = None,
    ) -> np.ndarray:
        """Compute Cartesian pose [x, y, z, alpha, beta, gamma] in [mm | deg]."""
        T = self.forward_transform(joints_deg, T_flange_tcp=T_flange_tcp)
        pos = np.where(np.isclose(T[:3, 3], 0.0, atol=1e-9), 0.0, T[:3, 3])
        eul = rot_to_mecademic_euler(T[:3, :3])
        return np.concatenate([pos, eul])


SESSION2_TEST_CONFIGS: list[list[float]] = [
    [0, 0, 0, 0, 0, 0],
    [90, 0, 0, 0, 0, 0],
    [0, 0, -90, 0, 0, 0],
    [0, 90, -90, 0, 0, 0],
    [0, 0, 0, 90, 0, 0],
    [0, 0, 0, 0, 90, 0],
    [0, 0, 0, 0, 0, 90],
]


if __name__ == "__main__":
    _, T_simple = build_symbolic_fk_simple(align_to_frf=True)
    _, T_dh = build_symbolic_fk_dh(align_to_frf=True)
    print("Simple frame placement == Craig DH (aligned to FRF):", sp.simplify(T_simple - T_dh) == sp.zeros(4, 4))

    kin = Meca500Kinematics(method="simple", align_to_frf=True)
    print("\nSession 2.2 Forward Kinematics [x, y, z, alpha, beta, gamma] in [mm | deg]:")
    for q in SESSION2_TEST_CONFIGS:
        pose = np.round(kin.forward_pose(q), 4)
        print(f"  q = {str(q):22s} -> {pose.tolist()}")
