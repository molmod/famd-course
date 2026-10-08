"""Utilities for setting up simulations with non-standard residues in OpenMM."""

import numpy as np

__all__ = ["convert_sdf_to_pdb"]


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
    implementation, not meant to be easily extensible to other formats etc. It
    will not handle broken SDF files gracefully either. All atoms are put in one
    residue and one chain.

    """
    if len(resname) > 3:
        raise ValueError("Residue name too long.")
    # Read the relevant SDF data.
    with open(fn_sdf) as f:
        # Skip the header block.
        next(f)
        next(f)
        next(f)
        # The V2000 format has fixed-width columns. Fields are not always
        # separated by whitespace, e.g. when there are more than 99 atoms.
        line = next(f)
        natom = int(line[0:3])
        nbond = int(line[3:6])
        # Atomic positions in angstroms.
        atcoords = np.zeros((natom, 3), float)
        atsymbols = []
        for iatom in range(natom):
            line = next(f)
            atcoords[iatom] = line[0:10], line[10:20], line[20:30]
            atsymbols.append(line[31:34].strip())
        # Bonds with atom indexes starting at 1.
        # Format of one row: [first atom, second atom, integer bond order]
        bonds = np.zeros((nbond, 3), int)
        for ibond in range(nbond):
            line = next(f)
            bonds[ibond] = line[0:3], line[3:6], line[6:9]

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
            " ",
            "{:<4s}",
            " ",
            "{:<3s} ",
            "A",
            "   1",
            "    ",
            "{:8.3f}",
            "{:8.3f}",
            "{:8.3f}",
            "  1.00",
            "  0.00",
            "          ",
            "{:>2s}",
            "\n",
        ]
    )
    with open(fn_pdb, "w") as f:
        symbol_counters = {}
        for iatom, (atcoord, atsymbol) in enumerate(zip(atcoords, atsymbols, strict=True)):
            c = symbol_counters.get(atsymbol, 0) + 1
            symbol_counters[atsymbol] = c
            atname = f"{atsymbol.upper()}{c}"
            # Atom names of single-letter elements start in the second column of the
            # atom name field, unless the name has four characters.
            if len(atsymbol) == 1 and len(atname) < 4:
                atname = " " + atname
            f.write(
                hetatm_template.format(
                    iatom + 1,
                    atname,
                    resname,
                    atcoord[0],
                    atcoord[1],
                    atcoord[2],
                    atsymbol.upper(),
                )
            )
        for iatom, ineighs in sorted(neighbors.items()):
            f.write(
                "CONECT{:5d}{:s}\n".format(iatom, "".join(f"{ineigh:5d}" for ineigh in ineighs))
            )
        f.write("END\n")
