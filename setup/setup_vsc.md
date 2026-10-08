# FAMD Course Setup on VSC

All students are recommended to work with a standard Python setup
on the [UGent high-performance clusters](https://www.ugent.be/hpc/en),
which are part of the [Flemish Supercomputer Center (VSC)](https://www.vscentrum.be/).
General instructions for this setup can be found in the
[`getting-started`](https://github.ugent.be/PhyStack/getting-started/tree/main) repository.
This setup is reused by several courses in the Physics and Astronomy program.

After you've gone through these general `getting-started` instruction,
you will have learned the following:

- How to run Jupyter Notebooks in VSCode that run on the VSC clusters.
- How to open and use a virtual terminal on the same clusters.
- How to start an interactive job on the Donphan cluster.
- How to activate the newly installed software environment
  in the `${VSC_SCRATCH}/phystack/` directory.
- A few basic Linux commands that can be used in the terminal.

Afterward you are ready to download the tutorials for the FAMD course using the instructions below.
These are commands to be entered in a tmux session running on Donphan,
in the same fashion as the commands used to initialize the PhyStack environment.

- Change to the `phystack` directory:

    ```bash
    cd ${VSC_SCRATCH}/phystack/
    ```

- Activate the software environment

    ```bash
    v
    ```

- Make a new directory for the course and enter it:

    ```bash
    # ${VSC_SCRATCH}/phystack/
    mkdir famd
    cd famd
    ```

- Download a snapshot of the `famd-course` repository:

    ```bash
    # ${VSC_SCRATCH}/phystack/famd/
    wget https://github.com/molmod/famd-course/archive/refs/heads/main.zip
    ```

- Unpack the ZIP file:

    ```bash
    # ${VSC_SCRATCH}/phystack/famd/
    unzip main.zip
    ```

The getting started repository has [detailed instructions](https://github.ugent.be/PhyStack/getting-started/blob/main/docs/setup_vsc.md#test-the-vscode-tunnel)
for how to open the notebooks in the unzipped archive via [login.hpc.ugent.be](https://login.hpc.ugent.be).
