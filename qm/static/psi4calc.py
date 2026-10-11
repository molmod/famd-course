#!/usr/bin/env python3
"""Psi4 calculations on a single molecule: geometry optimization and MBIS charges.

Psi4 uses all CPU cores available to the process,
so the steps calling this script should not run in parallel.
Psi4 writes a file timer.dat in the current directory when it exits.
"""

import json
import logging
import os

import numpy as np
import psi4
from geometric.nifty import RawFileHandler
from stepup.core.call import driver

MEMORY = "8 GB"
"""Memory available to Psi4."""

GRID = (99, 590)
"""Number of radial and spherical points of the DFT and MBIS grids.

With the default DFT grid of Psi4 (75, 302), the analytic gradient is not always consistent
with the energy at the level of the convergence criteria of the geometry optimization.
"""


def _load_sdf(path_sdf: str) -> tuple[list[str], np.ndarray, int]:
    """Load the element symbols, Cartesian coordinates (Angstrom) and total charge from an SDF file.

    Only the first molecule in the file is read, which must be in the V2000 format.
    The total charge is the sum of the formal charges on the `M  CHG` lines.
    """
    with open(path_sdf) as fh:
        lines = fh.read().splitlines()
    natom = int(lines[3][0:3])
    nbond = int(lines[3][3:6])
    symbols = []
    positions = []
    for line in lines[4 : 4 + natom]:
        positions.append([float(line[0:10]), float(line[10:20]), float(line[20:30])])
        symbols.append(line[31:34].strip())
    charge = 0
    for line in lines[4 + natom + nbond :]:
        if line.startswith("M  END"):
            break
        if line.startswith("M  CHG"):
            words = line.split()
            charge += sum(int(word) for word in words[4::2])
    return symbols, np.array(positions), charge


def _load_xyz(path_xyz: str) -> tuple[list[str], np.ndarray]:
    """Load the element symbols and Cartesian coordinates (Angstrom) from an XYZ file."""
    with open(path_xyz) as fh:
        natom = int(next(fh))
        next(fh)
        symbols = []
        positions = []
        for _ in range(natom):
            words = next(fh).split()
            symbols.append(words[0])
            positions.append([float(word) for word in words[1:4]])
    return symbols, np.array(positions)


def _dump_xyz(path_xyz: str, symbols: list[str], positions: np.ndarray, comment: str):
    """Write an XYZ file with Cartesian coordinates in Angstrom."""
    with open(path_xyz, "w") as fh:
        print(len(symbols), file=fh)
        print(comment, file=fh)
        for symbol, (x, y, z) in zip(symbols, positions, strict=True):
            print(f"{symbol:2s} {x:15.10f} {y:15.10f} {z:15.10f}", file=fh)


def _setup(
    path_out: str, symbols: list[str], positions: np.ndarray, charge: int, basis: str
) -> psi4.core.Molecule:
    """Initialize Psi4 and return the (closed-shell) molecule."""
    psi4.core.set_output_file(path_out, False)
    psi4.set_memory(MEMORY)
    psi4.set_num_threads(len(os.sched_getaffinity(0)))
    psi4.set_options(
        {
            "basis": basis,
            "scf_type": "df",
            "reference": "rks",
            "e_convergence": 1e-8,
            "d_convergence": 1e-8,
            "dft_radial_points": GRID[0],
            "dft_spherical_points": GRID[1],
        }
    )
    lines = [f"{charge} 1"]
    for symbol, (x, y, z) in zip(symbols, positions, strict=True):
        lines.append(f"{symbol} {x:.10f} {y:.10f} {z:.10f}")
    lines.extend(["units angstrom", "symmetry c1", "no_com", "no_reorient"])
    return psi4.geometry("\n".join(lines))


def _symbols(molecule: psi4.core.Molecule) -> list[str]:
    """Return the element symbols of the molecule."""
    return [molecule.symbol(i).capitalize() for i in range(molecule.natom())]


def _positions(molecule: psi4.core.Molecule) -> np.ndarray:
    """Return the Cartesian coordinates of the molecule in Angstrom."""
    return molecule.geometry().np * psi4.constants.bohr2angstroms


def _dihedral(positions: np.ndarray, indices: list[int]) -> float:
    """Return the dihedral angle (degrees) of four atoms, given by indices counting from 0."""
    p0, p1, p2, p3 = positions[indices]
    b1 = (p2 - p1) / np.linalg.norm(p2 - p1)
    v = (p0 - p1) - np.dot(p0 - p1, b1) * b1
    w = (p3 - p2) - np.dot(p3 - p2, b1) * b1
    return np.degrees(np.arctan2(np.dot(np.cross(b1, v), w), np.dot(v, w)))


def opt(inp: list[str], out: list[str], method: str, basis: str, frozen: list[list[int]]):
    """Optimize the geometry of a molecule with geomeTRIC.

    Parameters
    ----------
    inp
        The SDF file with the initial geometry and the formal charges.
    out
        The XYZ file with the optimized geometry, the Psi4 output file and the geomeTRIC log file.
        The geomeTRIC log contains details of each optimization step,
        including the constraint violations (larger than 0.001 degrees).
    method
        The DFT functional.
    basis
        The basis set.
    frozen
        Dihedral angles to keep fixed at their initial values during the optimization.
        Each dihedral is given by four atom indices, counting from 1 as in the SDF file.
    """
    (path_sdf,) = inp
    path_opt_xyz, path_out, path_log = out
    symbols, positions, charge = _load_sdf(path_sdf)
    molecule = _setup(path_out, symbols, positions, charge, basis)
    psi4.set_options({"g_convergence": "gau", "geom_maxiter": 200})
    # geomeTRIC counts atoms from 0.
    frozen = [[i - 1 for i in d] for d in frozen]
    constraints = {"freeze": [{"type": "dihedral", "indices": d} for d in frozen]}
    # Psi4 does not configure the logger of geomeTRIC, so its messages would be discarded.
    logger = logging.getLogger("geometric")
    handler = RawFileHandler(path_log, mode="w")
    logger.addHandler(handler)
    try:
        energy = psi4.optimize(
            method,
            molecule=molecule,
            engine="geometric",
            optimizer_keywords={"constraints": constraints} if frozen else {},
        )
    finally:
        logger.removeHandler(handler)
        handler.close()
    comment = f"{method}/{basis} optimized geometry, charge {charge}, energy {energy:.10f} Eh"
    _dump_xyz(path_opt_xyz, _symbols(molecule), _positions(molecule), comment)
    if frozen:
        print("Frozen dihedral angles (degrees): initial, optimized, difference")
        for d in frozen:
            label = "-".join(f"{symbols[i]}{i + 1}" for i in d)
            phi0 = _dihedral(positions, d)
            phi1 = _dihedral(_positions(molecule), d)
            delta = (phi1 - phi0 + 180) % 360 - 180
            print(f"  {label:20s} {phi0:10.4f} {phi1:10.4f} {delta:+.1e}")


def mbis(inp: list[str], out: list[str], method: str, basis: str):
    """Compute MBIS charges and atomic multipoles of a molecule.

    Parameters
    ----------
    inp
        The SDF file (for the formal charges) and the XYZ file with the (optimized) geometry.
    out
        A JSON file with the results and the Psi4 output file.
        All results in the JSON file are in atomic units, except for the positions in Angstrom.
        The atomic quadrupoles have six components: xx, xy, xz, yy, yz, zz.
    method
        The DFT functional.
    basis
        The basis set.
    """
    path_sdf, path_xyz = inp
    path_json, path_out = out
    symbols_sdf, _, charge = _load_sdf(path_sdf)
    symbols, positions = _load_xyz(path_xyz)
    if symbols != symbols_sdf:
        raise ValueError(f"The atoms in {path_xyz} and {path_sdf} differ.")
    molecule = _setup(path_out, symbols, positions, charge, basis)
    psi4.set_options({"mbis_radial_points": GRID[0], "mbis_spherical_points": GRID[1]})
    energy, wfn = psi4.energy(method, molecule=molecule, return_wfn=True)
    psi4.oeprop(wfn, "DIPOLE", "MBIS_CHARGES", title="MBIS")
    charges = wfn.array_variable("MBIS CHARGES").np.ravel()
    result = {
        "method": method,
        "basis": basis,
        "charge": charge,
        "symbols": _symbols(molecule),
        "positions": _positions(molecule).tolist(),
        "energy": energy,
        "dipole": wfn.variable("MBIS DIPOLE").np.ravel().tolist(),
        "mbis_charges": charges.tolist(),
        "mbis_dipoles": wfn.array_variable("MBIS DIPOLES").np.tolist(),
        "mbis_quadrupoles": wfn.array_variable("MBIS QUADRUPOLES").np.tolist(),
        "mbis_valence_widths": wfn.array_variable("MBIS VALENCE WIDTHS").np.ravel().tolist(),
    }
    with open(path_json, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    print(f"MBIS charges ({method}/{basis}), sum = {charges.sum():+.6f}")
    for symbol, q in zip(result["symbols"], charges, strict=True):
        print(f"  {symbol:2s} {q:+.4f}")


if __name__ == "__main__":
    driver()
