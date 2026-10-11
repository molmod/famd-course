#!/usr/bin/env python3
"""Check the optimized geometries and compare MBIS with AM1-BCC charges.

One-off analysis, not part of the StepUp workflow (it needs RDKit and the OpenFF toolkit).
Run from qm/ after the workflow has completed:

    python check.py

For every molecule, it reports:

- all dihedral angles of rotatable bonds, before and after the optimization,
  to verify that the optimization stayed in the conformer of the initial geometry,
- intramolecular contacts between polar hydrogens and N or O atoms shorter than 2.5 Angstrom,
  which may indicate intramolecular hydrogen bonds,
- the MBIS charges in the tutorials, compared with the AM1-BCC charges of Sage 2.2.1,
  averaged over topologically equivalent atoms (as in static/export.py).
"""

import json

import numpy as np
from openff.toolkit import Molecule
from plan import FROZEN, TUTORIAL_DIR
from rdkit import Chem
from rdkit.Chem import rdMolTransforms

NAMES = ["ibuprofen", "aspirin", "amoxicillin", "dmso"]
CONTACT = 2.5
"""Distance threshold (Angstrom) for contacts between polar hydrogens and N or O atoms."""


def load_xyz(path: str) -> tuple[list[str], np.ndarray]:
    with open(path) as fh:
        lines = fh.read().splitlines()
    natom = int(lines[0])
    words = [line.split() for line in lines[2 : 2 + natom]]
    return [w[0] for w in words], np.array([[float(x) for x in w[1:4]] for w in words])


def with_positions(rdmol: Chem.Mol, positions: np.ndarray) -> Chem.Mol:
    """Return a copy of an RDKit molecule with new positions (Angstrom)."""
    rdmol = Chem.Mol(rdmol)
    conf = rdmol.GetConformer()
    for i, xyz in enumerate(positions):
        conf.SetAtomPosition(i, xyz.tolist())
    return rdmol


def label(rdmol: Chem.Mol, i: int) -> str:
    return f"{rdmol.GetAtomWithIdx(i).GetSymbol()}{i + 1}"


def rotatable_dihedrals(rdmol: Chem.Mol) -> list[tuple[int, int, int, int]]:
    """One dihedral per acyclic single bond between non-terminal atoms.

    The outer atoms are the heaviest neighbors (lowest index in case of a tie).
    """
    pattern = Chem.MolFromSmarts("[!D1]-&!@[!D1]")
    result = []
    for i1, i2 in rdmol.GetSubstructMatches(pattern):
        outer = []
        for center, other in (i1, i2), (i2, i1):
            neighbors = [
                n.GetIdx()
                for n in rdmol.GetAtomWithIdx(center).GetNeighbors()
                if n.GetIdx() != other
            ]
            outer.append(min(neighbors, key=lambda i: (-rdmol.GetAtomWithIdx(i).GetAtomicNum(), i)))
        result.append((outer[0], i1, i2, outer[1]))
    return result


def polar_contacts(rdmol: Chem.Mol) -> list[str]:
    """Short distances between polar hydrogens and N or O atoms, at least three bonds apart."""
    pos = rdmol.GetConformer().GetPositions()
    dm = Chem.GetDistanceMatrix(rdmol)
    result = []
    for h in rdmol.GetAtoms():
        if h.GetSymbol() != "H" or h.GetNeighbors()[0].GetSymbol() not in ("N", "O"):
            continue
        for a in rdmol.GetAtoms():
            if a.GetSymbol() not in ("N", "O") or dm[h.GetIdx(), a.GetIdx()] <= 3:
                continue
            distance = np.linalg.norm(pos[h.GetIdx()] - pos[a.GetIdx()])
            if distance < CONTACT:
                result.append(
                    f"{label(rdmol, h.GetIdx())}...{label(rdmol, a.GetIdx())} {distance:.2f}"
                )
    return result


def main():
    for name in NAMES:
        print(f"=== {name}")
        rdmol0 = Chem.MolFromMolFile(f"static/{name}.sdf", removeHs=False)
        symbols, pos_opt = load_xyz(f"output/{name}/opt/opt.xyz")
        if symbols != [a.GetSymbol() for a in rdmol0.GetAtoms()]:
            raise ValueError(f"Atom order of {name} changed.")
        rdmol1 = with_positions(rdmol0, pos_opt)
        conf0, conf1 = rdmol0.GetConformer(), rdmol1.GetConformer()

        print("Dihedral angles of rotatable bonds (initial -> optimized):")
        frozen = [tuple(i - 1 for i in d) for d in FROZEN.get(name, [])]
        rotatable = rotatable_dihedrals(rdmol0)
        for dihedral in rotatable + [d for d in frozen if d not in rotatable]:
            tau0 = rdMolTransforms.GetDihedralDeg(conf0, *dihedral)
            tau1 = rdMolTransforms.GetDihedralDeg(conf1, *dihedral)
            change = (tau1 - tau0 + 180) % 360 - 180
            note = " (frozen)" if dihedral in frozen else ""
            note += " LARGE CHANGE" if abs(change) > 45 else ""
            atoms = "-".join(label(rdmol0, i) for i in dihedral)
            print(f"  {atoms:24s} {tau0:+7.1f} -> {tau1:+7.1f}{note}")
        print(f"Polar contacts < {CONTACT} A, initial: {polar_contacts(rdmol0) or 'none'}")
        print(f"Polar contacts < {CONTACT} A, optimized: {polar_contacts(rdmol1) or 'none'}")

        with open(f"output/{name}/mbis/mbis.json") as fh:
            mbis = json.load(fh)
        q_raw = np.array(mbis["mbis_charges"])
        q_mbis = Molecule.from_file(f"{TUTORIAL_DIR}{name}.sdf").partial_charges.m
        molecule = Molecule.from_file(f"static/{name}.sdf")
        molecule.assign_partial_charges("am1bcc")
        q_bcc = molecule.partial_charges.m
        print(f"Sum of raw MBIS charges: {q_raw.sum():+.4f}")
        print(f"{'atoms':18s} {'AM1-BCC':>8s} {'MBIS':>8s} {'diff':>8s} {'MBIS spread':>12s}")
        ranks = list(Chem.CanonicalRankAtoms(rdmol0, breakTies=False, includeChirality=False))
        for rank in sorted(set(ranks), key=ranks.index):
            cls = [i for i, r in enumerate(ranks) if r == rank]
            atoms = ",".join(label(rdmol0, i) for i in cls)
            print(
                f"{atoms:18s} {q_bcc[cls].mean():+8.3f} {q_mbis[cls].mean():+8.3f} "
                f"{q_mbis[cls].mean() - q_bcc[cls].mean():+8.3f} {np.ptp(q_raw[cls]):12.3f}"
            )
        print()


if __name__ == "__main__":
    main()
