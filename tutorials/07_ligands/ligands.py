"""Utilities for setting up simulations with non-standard residues in OpenMMM."""

import mdtraj
import numpy as np

__all__ = ["convert_sdf_to_pdb", "estimate_volume"]


def convert_sdf_to_pdb(fn_sdf, fn_pdb, resname="UNL"):
    """Convert an SDF file (from PubChem, ChemDraw, ...) to a proper PDB file.

    Parameters
    ----------
    fn_sdf
        Path of the SDF file, must exist.
    fn_pdb
        Path of the PDB file. If it exists, it will be overwritten.
    resname
        The residue name in the PDB file. Maximum 3 characters.

    Notes
    -----
    Openbabel can also perform this type of conversion, but generally does a
    poor job on the atom names in the PDB file. This is a one-off
    implementation, not meant to be easily extendible to other formats etc. It
    will not handle broken SDF files gracefully either. All atoms are put in one
    residue and one chain.

    """
    if len(resname) > 3:
        raise ValueError("Residue name too long.")
    # Read the relevant SDF data.
    with open(fn_sdf) as f:
        # skip a few lines
        next(f)
        next(f)
        next(f)
        words = next(f).split()
        natom = int(words[0])
        nbond = int(words[1])
        # atomic positions in angstroms
        atcoords = np.zeros((natom, 3), float)
        atsymbols = []
        for iatom in range(natom):
            words = next(f).split()
            atcoords[iatom] = words[:3]
            atsymbols.append(words[3])
        # bonds with atom indexes starting at 1.
        # fomat of one row: [first atom, second atom, integer bond order]
        bonds = np.zeros((nbond, 3), int)
        for ibond in range(nbond):
            words = next(f).split()
            bonds[ibond] = words[:3]

    # Convert bonds to neighbour dictionary, needed for the CONECT lines in PDB.
    neighbors = {}
    for ia, ib, bo in bonds:
        neighbors.setdefault(ia, []).extend([ib] * bo)
        neighbors.setdefault(ib, []).extend([ia] * bo)

    # Write the PDB file
    hetatm_template = "".join(
        [
            "HETATM",
            "{:5d}",
            "{:>4s} ",
            " ",
            "{:<3s} ",
            "A",
            "   1",
            "    ",
            "{:8.3f}",
            "{:8.3f}",
            "{:8.3f}",
            "  0.00",
            "  0.00",
            "          ",
            "{:>2s}",
            "\n",
        ]
    )
    with open(fn_pdb, "w") as f:
        symbol_counters = {}
        for iatom, (atcoord, atsymbol) in enumerate(zip(atcoords, atsymbols, strict=False)):
            c = symbol_counters.get(atsymbol, 0) + 1
            symbol_counters[atsymbol] = c
            atname = f"{atsymbol}{c}"
            f.write(
                hetatm_template.format(
                    iatom + 1,
                    atname,
                    resname,
                    atcoord[0],
                    atcoord[1],
                    atcoord[2],
                    atsymbol,
                )
            )
        for iatom, ineighs in sorted(neighbors.items()):
            f.write(
                "CONECT{:5d}{:s}\n".format(iatom, "".join(f"{ineigh:5d}" for ineigh in ineighs))
            )
        f.write("END\n")


def estimate_volume(fn_pdb):
    """Estimate an upper bound for the molecular volume, given a PDB file."""
    # Load Cartesian coordinates in Angstrom.
    traj_single = mdtraj.load(fn_pdb)
    xyz = traj_single.xyz[0] * 10
    # Get array with vdW radii
    vdw_radii = np.array([atom.element.radius for atom in traj_single.top.atoms]) * 10
    # Estimate the width in various directions and derive an average volume.
    nrep = 1000
    radii = np.zeros(nrep)
    for irep in range(nrep):
        unit = np.random.normal(0, 1, 3)
        unit /= np.linalg.norm(unit)
        tf = np.dot(xyz, unit)
        low = (tf - vdw_radii).min()
        high = (tf + vdw_radii).max()
        radii[irep] = (high - low) / 2
    # Compute average volume
    return ((4 / 3) * np.pi * radii**3).mean()
