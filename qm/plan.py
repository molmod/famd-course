#!/usr/bin/env python3
"""StepUp workflow of the MBIS charges used in the ligand tutorials, see README.md.

For each molecule `static/<name>.sdf`, Psi4 optimizes the geometry with a small basis set
(`output/<name>/opt/`) and then computes MBIS charges at the optimized geometry
with a larger basis set (`output/<name>/mbis/`).
The charges are finally written to an SDF file in `../tutorials/07_ligands/mbis_charges/`.
The molecules in `static/test/` are only optimized, to test the frozen dihedral angles.
Psi4 uses all CPU cores, so the steps are meant to be executed one at a time (`stepup build -j 1`).
"""

from pathlib import Path

from stepup.core.api import call, static

METHOD = "b3lyp"
"""The DFT functional."""

OPT_BASIS = "def2-svp"
"""The basis set of the geometry optimization: split valence with polarization functions."""

MBIS_BASIS = "def2-tzvpd"
"""The basis set of the MBIS calculation: triple zeta with polarization and diffuse functions."""

FROZEN = {
    # Without constraints, the amine group rotates towards the amide oxygen in the gas phase,
    # forming an intramolecular hydrogen bond that is unlikely in a polar solvent.
    "amoxicillin": [[9, 19, 18, 5], [38, 9, 19, 18]],
    # Test case: H3-C1-C2-H6 is 75 degrees in the initial geometry, 15 degrees away from staggered.
    "ethane": [[3, 1, 2, 6]],
}
"""Dihedral angles kept fixed in the geometry optimization (atom indices counting from 1)."""

TO_QM = "../../../"
"""Relative path from a calculation directory (output/<name>/<calc>/) to qm/."""

TUTORIAL_DIR = "../tutorials/07_ligands/mbis_charges/"
"""Directory where the final SDF files with MBIS charges are written."""


def opt(psi4calc: str, path_sdf: Path):
    """Optimize the geometry of a molecule in output/<name>/opt/."""
    name = path_sdf.stem
    call(
        psi4calc,
        "opt",
        workdir=f"output/{name}/opt/",
        inp=f"{TO_QM}{path_sdf}",
        out=["opt.xyz", "psi4.out", "geometric.log"],
        vol="timer.dat",
        method=METHOD,
        basis=OPT_BASIS,
        frozen=FROZEN.get(name, []),
    )


def main():
    static("static/psi4calc.py", "static/export.py")
    psi4calc = f"{TO_QM}static/psi4calc.py"
    for path_sdf in static("static/test/*.sdf"):
        opt(psi4calc, path_sdf)
    for path_sdf in static("static/*.sdf"):
        name = path_sdf.stem
        opt(psi4calc, path_sdf)
        call(
            psi4calc,
            "mbis",
            workdir=f"output/{name}/mbis/",
            inp=[f"{TO_QM}{path_sdf}", "../opt/opt.xyz"],
            out=["mbis.json", "psi4.out"],
            vol="timer.dat",
            method=METHOD,
            basis=MBIS_BASIS,
        )
        call(
            "static/export.py",
            "export",
            inp=[path_sdf, f"output/{name}/mbis/mbis.json"],
            out=f"{TUTORIAL_DIR}{name}.sdf",
            name=name,
            method=f"{METHOD}/{MBIS_BASIS} // {METHOD}/{OPT_BASIS}",
        )


if __name__ == "__main__":
    main()
