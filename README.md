[![License: CC BY-NC 4.0](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Status of the pre-commit hooks](https://results.pre-commit.ci/badge/github/molmod/famd-course/main.svg)](https://results.pre-commit.ci/latest/github/molmod/famd-course/main)


# Tutorials for "Foundations and Applications of Molecular Dynamics"

## Scope

This repository contains tutorials for the course [Foundations and Applications of Molecular Dynamics](https://studiekiezer.ugent.be/2026/studiefiche/en/C004662), an introductory elective course in the M.Sc. program [Biochemistry and Biotechnology](https://studiekiezer.ugent.be/2026/master-of-science-in-biochemistry-and-biotechnology-en) at [Ghent University](https://www.ugent.be/en).
The materials are also open to anyone interested in learning molecular dynamics with [OpenMM](https://openmm.org/).

The course is designed for students with a background in the life sciences rather than in physics.
No prior knowledge of statistical mechanics is assumed:
the aim is to give you the practical skills and the essential theory to run valid molecular dynamics simulations and to interpret their results with confidence.
The tutorials assume you have a basic knowledge of [Python](https://www.python.org/).

## Getting Started

1. The [setup/](setup/) folder contains instructions to set up the software environment for running the tutorials.

2. The [tutorials/](tutorials/) folder contains the Jupyter notebooks, which are best followed more or less in order:

   1. First steps: water and Lennard-Jones systems
   2. Force fields, applied to alanine dipeptide
   3. Running demanding notebooks as non-interactive jobs on an HPC cluster
   4. A short protein simulation (villin headpiece)
   5. Analysis of MD trajectories
   6. Visualization
   7. Ligands, using ibuprofen as an example

   See [tutorials/README.md](tutorials/README.md) for links to the individual notebooks.

A GPU is recommended but not required.
OpenMM is highly optimized for GPUs, which typically run simulations about 100 times faster than a regular CPU.
All tutorials can also be completed on a CPU.

## Questions and Feedback

- UGent students can ask questions on the [Ufora course page](https://ufora.ugent.be/d2l/home/1387689).
- Anyone, including UGent students, can also ask questions or report problems on the [issue tracker](https://github.com/molmod/famd-course/issues).

Use whichever channel you feel most comfortable with.

## Contributing

Contributions are welcome, from small corrections and clarifications to improved setup instructions for your operating system.
See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## Authors

The course materials are written and maintained by Toon Verstraelen,
and includes contributions from Jelle Vekeman.

## License

All files in this repository are licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

The software installed by following the setup instructions (OpenMM and other packages) is distributed under its own licenses.
