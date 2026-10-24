# Tutorials for "Foundations and Applications of Molecular Dynamics"

(See top-level [README.md](../README.md) for license and scope.)

## Overview

The tutorials consist of the following sections, to be followed more or less in order:

**1. First steps:**

- [01_first_steps/01_water.ipynb](01_first_steps/01_water.ipynb)
- [01_first_steps/02_lennard_jones.ipynb](01_first_steps/02_lennard_jones.ipynb)

**2. Different ways of simulating alanine dipeptide:**

- [02_alanine_dipeptide/01_force_fields.ipynb](02_alanine_dipeptide/01_force_fields.ipynb)

**3. Run demanding OpenMM notebooks as a non-interactive job:**

- [03_noninteractive/01_noninteractive_notebook_on_hpc.ipynb](03_noninteractive/01_noninteractive_notebook_on_hpc.ipynb)

**4. A short protein MD simulation:**

- [04_protein/01_villin_headpiece.ipynb](04_protein/01_villin_headpiece.ipynb)

**5. Analysis of MD trajectories:**

These tutorials use the outputs from the previous tutorial and assume that it has been run successfully.

- [05_analysis/01_internal_coordinates_averages.ipynb](05_analysis/01_internal_coordinates_averages.ipynb)
- [05_analysis/02_physicochemical_properties.ipynb](05_analysis/02_physicochemical_properties.ipynb)
- [05_analysis/03_alignment_principal_component_analysis.ipynb](05_analysis/03_alignment_principal_component_analysis.ipynb)

**6. Restart a simulation from a saved state:**

- [06_restart/01_restart_from_saved_state.ipynb](06_restart/01_restart_from_saved_state.ipynb)

**7. Ligands:**

- [07_ligands/01_ibuprofen_gas_phase.ipynb](07_ligands/01_ibuprofen_gas_phase.ipynb)
- [07_ligands/02_ibuprofen_solvent.ipynb](07_ligands/02_ibuprofen_solvent.ipynb)

**8. Transport properties: ionic conductivity of aqueous sodium acetate:**

- [08_transport/01_npt_equilibration.ipynb](08_transport/01_npt_equilibration.ipynb)
- [08_transport/02_nvt_production.ipynb](08_transport/02_nvt_production.ipynb)
- [08_transport/03_conductivity_analysis.ipynb](08_transport/03_conductivity_analysis.ipynb)

## Online resources

The tutorials are strongly inspired by several online resources (tutorials, documentation and examples) from the OpenMM, Python, NumPy, Matplotlib and other projects.
The main references are:

* OpenMM website: http://openmm.org/
* OpenMM Users Guide: http://docs.openmm.org/latest/userguide/index.html
* Python website: https://www.python.org/
* Python tutorial: https://docs.python.org/3/tutorial/index.html
* NumPy website: https://numpy.org/
* NumPy User Guide: https://docs.scipy.org/doc/numpy/user/index.html
* Matplotlib website: https://matplotlib.org/
* nglview: http://nglviewer.org/nglview/latest/
* MDTraj: http://mdtraj.org/

Even though these resources contain all the background and details to learn OpenMM and related tools, the amount of information is simply overwhelming.
The aim of the tutorials is to provide a gentle introduction to many of the topics in the above references.
