#!/usr/bin/env python3
"""Write the MBIS charges of a molecule to an SDF file for the tutorials.

The charges in the SDF file are:

1. averaged over topologically equivalent atoms (e.g. the three hydrogens of a methyl group),
2. shifted uniformly so that they add up to the total charge of the molecule.

The SDF file contains the bonds and formal charges of the original SDF file from PubChem,
the optimized geometry and the partial charges as an atom property list,
which can be loaded with `openff.toolkit.Molecule.from_file`.
"""

import json

import numpy as np
from stepup.core.call import driver


def _load_sdf(path_sdf: str) -> tuple[str, str, list[str], list[str], int, list[str]]:
    """Load the relevant parts of the first molecule in an SDF file in the V2000 format.

    Returns
    -------
    title
        The first line of the file. (PubChem puts the compound ID here.)
    counts_line
        The fourth line of the file, with the numbers of atoms and bonds.
    atom_lines
        The lines of the atom block.
    bond_lines
        The lines of the bond block.
    charge
        The total charge, i.e. the sum of the formal charges on the `M  CHG` lines.
    property_lines
        All lines after the bond block, up to and including `M  END`.
    """
    with open(path_sdf) as fh:
        lines = fh.read().splitlines()
    natom = int(lines[3][0:3])
    nbond = int(lines[3][3:6])
    atom_lines = lines[4 : 4 + natom]
    bond_lines = lines[4 + natom : 4 + natom + nbond]
    property_lines = []
    charge = 0
    for line in lines[4 + natom + nbond :]:
        property_lines.append(line)
        if line.startswith("M  END"):
            break
        if line.startswith("M  CHG"):
            charge += sum(int(word) for word in line.split()[4::2])
    return lines[0], lines[3], atom_lines, bond_lines, charge, property_lines


def equivalent_atoms(symbols: list[str], bonds: list[tuple[int, int]]) -> list[list[int]]:
    """Group atoms that cannot be distinguished by the elements and the connectivity.

    Atoms are first labeled by their element.
    Then, labels are refined iteratively by including the labels of the neighbors,
    until the number of distinct labels no longer increases.

    Bond orders and formal charges are ignored, so that resonance structures are equivalent,
    e.g. the two sides of a benzene ring in a Kekule structure,
    or the two oxygen atoms of a carboxylate group.
    Stereochemistry is also ignored: e.g. the two methyl groups of an isopropyl group
    attached to a chiral carbon are treated as equivalent.

    Parameters
    ----------
    symbols
        Element symbols.
    bonds
        Pairs of bonded atoms, with atom indices counting from 0.

    Returns
    -------
    classes
        A list of lists of atom indices, one list for each group of equivalent atoms.
    """
    neighbors = [[] for _ in symbols]
    for iatom0, iatom1 in bonds:
        neighbors[iatom0].append(iatom1)
        neighbors[iatom1].append(iatom0)
    labels = list(symbols)
    while True:
        # Each new label combines the old label with the sorted labels of the neighbors.
        new = [
            (labels[i], tuple(sorted(labels[j] for j in neighbors[i]))) for i in range(len(labels))
        ]
        # Replace the (nested) labels by small integers to keep them compact.
        unique = {label: k for k, label in enumerate(sorted(set(new)))}
        new = [unique[label] for label in new]
        if len(unique) == len(set(labels)):
            break
        labels = new
    classes = {}
    for i, label in enumerate(labels):
        classes.setdefault(label, []).append(i)
    return list(classes.values())


def export(inp: list[str], out: list[str], name: str, method: str):
    """Write an SDF file with the optimized geometry and the MBIS charges.

    Parameters
    ----------
    inp
        The original SDF file and the JSON file with the MBIS results.
    out
        The SDF file with the optimized geometry and the MBIS charges.
    name
        The name of the molecule, used as the title in the SDF file.
    method
        A description of the level of theory, written to the comment line of the SDF file.
    """
    path_sdf, path_json = inp
    (path_out,) = out
    cid, counts_line, atom_lines, bond_lines, charge, property_lines = _load_sdf(path_sdf)
    with open(path_json) as fh:
        mbis = json.load(fh)
    symbols = [line[31:34].strip() for line in atom_lines]
    if symbols != mbis["symbols"]:
        raise ValueError(f"The atoms in {path_sdf} and {path_json} differ.")
    bonds = [(int(line[0:3]) - 1, int(line[3:6]) - 1) for line in bond_lines]

    # Average the charges over equivalent atoms and correct the total charge.
    charges = np.array(mbis["mbis_charges"])
    print(f"Sum of the MBIS charges: {charges.sum():+.6f}")
    for cls in equivalent_atoms(symbols, bonds):
        if len(cls) > 1:
            print(
                "Averaging over equivalent atoms "
                + " ".join(f"{symbols[i]}{i + 1}" for i in cls)
                + f": spread {np.ptp(charges[cls]):.4f}"
            )
        charges[cls] = charges[cls].mean()
    charges += (charge - charges.sum()) / len(charges)

    # Write the SDF file with the optimized geometry, keeping all other atom fields.
    with open(path_out, "w") as fh:
        print(name, file=fh)
        # Program line: the dimension code 3D must be in columns 21-22.
        print(f"  {'export':8s}{'':10s}3D", file=fh)
        print(f"MBIS charges, {method}, PubChem CID {cid.strip()}", file=fh)
        print(counts_line, file=fh)
        for line, (x, y, z) in zip(atom_lines, mbis["positions"], strict=True):
            print(f"{x:10.4f}{y:10.4f}{z:10.4f}{line[30:]}", file=fh)
        for line in bond_lines + property_lines:
            print(line, file=fh)
        print("> <atom.dprop.PartialCharge>", file=fh)
        print(" ".join(f"{q:.6f}" for q in charges), file=fh)
        print(file=fh)
        print("$$$$", file=fh)
    print(f"Charges written to {path_out} (sum {charges.sum():+.6f}):")
    for i, (symbol, q) in enumerate(zip(symbols, charges, strict=True)):
        print(f"  {symbol}{i + 1:<3d} {q:+.4f}")


if __name__ == "__main__":
    driver()
