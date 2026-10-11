# MBIS Charges for the Ligand Tutorials

(See top-level [README.md](../README.md) for license and scope.)

This directory documents how the partial charges in
[../tutorials/07_ligands/mbis_charges/](../tutorials/07_ligands/mbis_charges/) were computed.
These charges are an alternative to the AM1-BCC charges of the Sage force field
and are derived from DFT calculations with the Minimal Basis Iterative Stockholder (MBIS) method.
(See [10.1021/acs.jctc.6b00456](https://doi.org/10.1021/acs.jctc.6b00456) for details on MBIS.)

You do not need to run anything in this directory to follow the tutorials:
the results are included in the repository.
The workflow is meant for those who are curious about how such charges are obtained,
or who want to compute MBIS charges for other molecules.

## Molecules

The molecules are those used in the ligand tutorials, including the suggestions in the hands-on exercises.
The initial geometries `static/<name>.sdf` are the 3D conformers from PubChem, without modifications.
PubChem generates these conformers with the MMFF94s force field without electrostatic interactions,
which avoids intramolecular hydrogen bonds that would be unlikely in solution.
The atom order is the same as in the SDF files downloaded in the tutorials.

| File | Molecule | PubChem CID | Atoms | Remarks on the initial geometry |
| --- | --- | --- | --- | --- |
| `ibuprofen.sdf` | ibuprofen (neutral) | [3672](https://pubchem.ncbi.nlm.nih.gov/compound/3672) | 33 | syn carboxylic acid, isobutyl perpendicular to the ring |
| `aspirin.sdf` | aspirin (neutral) | [2244](https://pubchem.ncbi.nlm.nih.gov/compound/2244) | 21 | syn carboxylic acid, Z ester perpendicular to the ring |
| `amoxicillin.sdf` | amoxicillin (neutral) | [33613](https://pubchem.ncbi.nlm.nih.gov/compound/33613) | 44 | syn carboxylic acid, trans amide, two dihedrals frozen (see below) |
| `dmso.sdf` | dimethyl sulfoxide | [679](https://pubchem.ncbi.nlm.nih.gov/compound/679) | 10 | (rigid) |

Each file was downloaded with:

```bash
curl -o static/<name>.sdf "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/CID/<cid>/record/SDF/?record_type=3d&response_type=save"
```

Water is not included: the TIP3P charges are an integral part of the water model in Sage
and should not be replaced.

The initial geometries were checked with RDKit and MMFF94 before starting the DFT calculations:

- None of them contains a hydrogen bond donor closer than 2.7 Å to an acceptor
  (N or O, at least three bonds away).
- They are not strained: after a relaxation with MMFF94 and a dielectric constant of 80
  (a crude model of a polar solvent), each of them lies within 0.6 kcal/mol of the lowest
  of 300 conformers generated with RDKit.
- A gas-phase relaxation (MMFF94 with a dielectric constant of 1) leaves ibuprofen and aspirin in the same conformer.
  In amoxicillin, however, the amine group rotates towards the oxygen of the neighboring amide,
  forming an intramolecular N-H···O=C contact of 2.4 Å.
  Such a contact is unlikely in a polar solvent, where both groups are hydrogen-bonded to the solvent.
  Hence, the dihedral angles N9-C19-C18-O5 and H38-N9-C19-C18 are kept fixed
  at their initial values in the DFT geometry optimization (`FROZEN` in `plan.py`).

These molecules are simulated in their neutral form, as downloaded from PubChem.
In water at physiological pH, ibuprofen and aspirin are mostly deprotonated
and amoxicillin is mostly a zwitterion.

## Workflow

`plan.py` defines a [StepUp](https://reproducible-reporting.github.io/stepup-core/) workflow
with three steps for every `static/<name>.sdf`:

1. Geometry optimization at the B3LYP/def2-SVP level with Psi4 and geomeTRIC
   (`output/<name>/opt/opt.xyz`), using `static/psi4calc.py`.
2. Single-point calculation at the B3LYP/def2-TZVPD level on the optimized geometry,
   followed by MBIS partitioning (`output/<name>/mbis/mbis.json`), using `static/psi4calc.py`.
   The JSON file contains the MBIS charges, atomic dipoles and quadrupoles, valence widths,
   and the molecular dipole moment, in atomic units (except for the positions in Å).
3. Export of the charges to `../tutorials/07_ligands/mbis_charges/<name>.sdf`, using `static/export.py`.
   The charges are averaged over topologically equivalent atoms
   (e.g. the three hydrogens of a methyl group, or the two sides of a para-substituted benzene ring),
   because these atoms become equivalent in an MD simulation through internal rotations.
   They are then shifted uniformly so that they add up to the total charge of the molecule.
   The SDF file contains the optimized geometry, the bonds, and the charges as an atom property,
   which can be loaded with `openff.toolkit.Molecule.from_file`.

The optimization also writes the log of geomeTRIC to `output/<name>/opt/geometric.log`,
which Psi4 would otherwise discard.
After every step, this log lists the constraints that deviate more than 0.001 degrees from their target values.
geomeTRIC only considers the optimization converged when all constraints are satisfied within 0.01 degrees.
For molecules with frozen dihedral angles, `psi4calc.py` prints their initial and optimized values
(shown by StepUp).

The molecules in `static/test/` are only optimized (step 1), to test the setup.
Currently, this is a twisted ethane molecule (`static/test/ethane.sdf`),
whose H3-C1-C2-H6 dihedral angle is frozen at 75 degrees, 15 degrees away from the staggered conformer.

The DFT and MBIS calculations use a (99, 590) integration grid.
The total charge of each molecule is derived from the formal charges in the SDF file.
The Psi4 output of each calculation is written to `psi4.out` in the same directory.

## Running the Workflow

You need a Python environment with [Psi4](https://psicode.org/), [geomeTRIC](https://geometric.readthedocs.io/),
NumPy and StepUp, e.g. installed with conda or mamba from conda-forge.
Psi4 uses all CPU cores available to the process, so run StepUp with one job at a time:

```bash
stepup build -j 1
```

To test the frozen dihedral angles on the ethane example before running the full workflow:

```bash
stepup build -j 1 output/ethane/opt/opt.xyz
```

The wall times below are estimates for 8 cores.
They are extrapolated from similar calculations on smaller molecules:

| Molecule | Optimization | MBIS |
| --- | --- | --- |
| DMSO | ~1 min | ~1 min |
| aspirin | 10-20 min | ~5 min |
| ibuprofen | 0.5-1 h | ~10 min |
| amoxicillin | 1.5-4 h | 20-40 min |

To compute charges for another molecule, add its SDF file to `static/` and rerun the workflow.
Check the initial geometry carefully, as discussed above.

## Checking the Results

`check.py` (run from `qm/` with RDKit and the OpenFF toolkit, not part of the workflow) prints:

- the dihedral angles of all rotatable bonds before and after the optimization,
  to verify that the optimization stayed in the initial conformer,
- short contacts between polar hydrogens and N or O atoms,
- a comparison of the MBIS charges with the AM1-BCC charges of Sage.

## Using the Charges in OpenFF

The SDF files with MBIS charges can be used with the `charge_from_molecules` argument
of `ForceField.create_interchange`, e.g.:

```python
molecule = openff.toolkit.Molecule.from_file("mbis_charges/ibuprofen.sdf")
topology = molecule.to_topology()
force_field = openff.toolkit.ForceField("openff-2.2.1.offxml")
interchange = force_field.create_interchange(topology, charge_from_molecules=[molecule])
```

Use the molecule loaded from the SDF file with MBIS charges also to build the topology,
so that the atom order is the same.
With version 0.5.3 of OpenFF Interchange, `to_openmm_system()` assigns wrong charges
when the atom order of the molecule passed to `charge_from_molecules` differs from that in the topology.

Note that MBIS charges from gas-phase DFT calculations are not polarized by the solvent,
unlike the AM1-BCC charges, which were designed to mimic the (over)polarized HF/6-31G* charges in a condensed phase.
The Lennard-Jones parameters of Sage were fitted together with AM1-BCC charges,
so replacing the charges may affect the accuracy of the force field.

A related issue arises for ions, e.g. the deprotonated forms of ibuprofen and aspirin.
Ions in solution are often simulated with scaled charges, typically 0.75 to 0.85 times the formal charge
for small ions in water, or around 0.8 for ionic liquids.
The scaling is a crude way to account for electronic polarization and charge transfer,
which a fixed-charge force field with formal charges lacks.
A physical motivation is the *electronic continuum correction* (ECC)
of Leontyev and Stuchebrukhov ([10.1039/c0cp01971b](https://doi.org/10.1039/c0cp01971b)),
which treats electronic polarization as a uniform dielectric continuum.
The ionic charges are then screened by a factor $1/\sqrt{\epsilon_\text{el}}$,
where $\epsilon_\text{el}$ is the electronic (high-frequency) dielectric constant of the medium.
For water, $\epsilon_\text{el} \approx 1.78$, which gives a scaling factor of about 0.75.
Such models give better structural and transport properties than models with formal charges,
but no single scaling factor works for all properties.
Blazquez et al. ([10.1021/acs.jctc.3c00562](https://doi.org/10.1021/acs.jctc.3c00562))
argued that the scaled charges describe the potential energy surface,
whereas the formal (integer) charges still describe the dipole moment surface.
With a scaled-charge force field for NaCl and KCl in water,
they reproduced the experimental electrical conductivities
by running the dynamics with scaled charges and computing the conductivity with integer charges.
For ionic liquids, see the recent paper by Zaby et al. from the Kirchner group
([10.1002/cphc.70477](https://doi.org/10.1002/cphc.70477))
for a discussion of charge scaling and its effect on computed conductivities.
