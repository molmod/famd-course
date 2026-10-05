# Software Setup

(See top-level [README.md](../README.md) for license and scope.)

## Background

Practically all simulations in the tutorials are carried out with OpenMM,
which is described extensively [here](http://docs.openmm.org/latest/userguide/library.html).
In short, OpenMM is a modern open-source molecular simulation toolkit: it supports many popular (bio)molecular force fields (AMBER, CHARMM, AMOEBA, ...),
it supports GPU-accelerated calculations,
and it can carry out many types of advanced molecular dynamics simulations.

To access and customize all these features, and to write reproducible simulation protocols,
OpenMM simulations are implemented by writing Python scripts.
Hence, to install OpenMM, you need (to create) a Python environment and install OpenMM as a Python package.
(The C++ interface is not covered in this tutorial.)
All tutorials are implemented as Jupyter notebooks,
which you can run in Jupyter Lab or VSCode.

## Installation

There are two ways to set up the required software environment:

1. If you are following the course at Ghent University,
   you can use the [PhyStack](https://github.ugent.be/PhyStack/getting-started) environment,
   which is available on the [Tier-2 VSC cluster of Ghent University](https://www.ugent.be/hpc/).
   It is a pre-installed software module with OpenMM and many other scientific packages,
   and is used in several courses at Ghent University.

2. You can also set up your own environment,
   for which we recommend using [Mamba](https://mamba.readthedocs.io/en/latest/),
   which is a more efficient version of [Conda](https://docs.conda.io/en/latest/).
   Detailed instructions can be found in the [setup_mamba.md](setup_mamba.md) file.

The second option is more flexible but less optimized in terms of performance, which should not be critical for the tutorials.

With the second option, you can decide to install the software environment on your own laptop or on a high-performance computing (HPC) cluster.
Both routes have their strengths and weaknesses, which are summarized below.

### Tutorial notebooks on an HPC

**Strengths:**

- You have access to significant computational power, including GPUs.
- It is possible to have calculations running while your laptop is switched off.
- No software needs to be installed on your laptop,
  except for a web browser and optionally a secure shell client.
- For VSC users, most of the installation is already done for you.

**Weaknesses:**

- For non-VSC users, the installation can be tricky.
- Interactive jobs on a cluster have a pre-defined (by you) duration.
  Such sessions end without warning, at which point you may lose some of your work.
- You must remain connected to the Internet for interactive Jupyter notebooks.

### Tutorial notebooks on your laptop

**Strengths:**

- Calculations require no network.
  (Installation does.)
- Output files are stored locally.
  (They are easy to access, but it may also become a problem when they fill up your hard drive.)

**Weaknesses:**

- The installation requires a significant amount of work.
- We have never tested the setup instructions on Windows.
- Your laptop could overheat when running longer simulations.
- Your laptop must remain powered on during calculations.
  (Keep it plugged into a power socket, because intensive calculations quickly drain the battery.)
