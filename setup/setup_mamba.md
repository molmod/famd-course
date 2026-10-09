# Software Setup with Mamba

To run OpenMM simulations on your laptop, we recommend using a standardized Python environment based on Conda.
These instructions show how to use a derivative of Anaconda, called **Miniforge**, for two reasons:

- Miniforge comes pre-configured with the [conda-forge](https://conda-forge.org/) software channel,
  which contains a larger selection of (scientific) software packages than the default Anaconda channel.
- Miniforge is more lightweight and comes with the [Mamba](https://mamba.readthedocs.io/en/latest/) package manager,
  a faster, drop-in reimplementation of the Conda package manager.

The instructions below are primarily tested on Linux,
and should also work on macOS and Windows Subsystem for Linux (WSL).
A native setup on Windows is currently untested.

## A Note on Virtual Terminals

The instructions below require you to enter commands in a [virtual terminal](https://en.wikipedia.org/wiki/Virtual_console),
the software equivalent of a [terminal computer](https://en.wikipedia.org/wiki/Computer_terminal) from the 1970s.
You type a text command, which is executed after you press `Enter`.
Possibly some output is shown as a result, but not always.
When the command completes, you can enter the next command.

Virtual terminals are powerful tools, but they are also picky!
Almost every character or whitespace you type does matter.
If a command prints some output, you must read and understand it before you continue with the next command.
Your previous command may have failed, in which case you should not continue with the next command, but try to fix the problem first.

These instructions assume that you are familiar with the basic usage of a virtual terminal.

## Installation

Take the following steps:

1. Download the [Miniforge installer](https://conda-forge.org/miniforge/)
   that matches the operating system and CPU architecture of your laptop.

    The following command, entered in a virtual terminal, selects the right installer automatically:

    ```bash
    curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
    ```

1. Run the Miniforge installer.

    In the same virtual terminal, in the same directory, enter the following command:

    ```bash
    bash "Miniforge3-$(uname)-$(uname -m).sh" -b
    ```

    Add the following line to your `~/.bashrc` (or `~/.bash_profile`) file (assuming that your terminal runs Bash):

    ```bash
    alias m='eval "$(${HOME}/miniforge3/bin/mamba shell hook --shell bash)"; mamba activate'
    ```

    If your terminal runs Zsh (the default on macOS),
    add the following line to `~/.zshrc` instead:

    ```bash
    alias m='eval "$(${HOME}/miniforge3/bin/mamba shell hook --shell zsh)"; mamba activate'
    ```

    We do not recommend the default behavior of Conda or Mamba, which activates the base environment in every new terminal through `~/.bashrc` (or `~/.zshrc`).
    Whenever you need it, just type `m` in a virtual terminal to activate the base environment of Miniforge.

    Close the terminal.

1. Start a (new) virtual terminal and activate the Miniforge environment
   by executing the alias `m`.

1. Configure Miniforge and install OpenMM (and other useful tools).

    Enter the following commands in the virtual terminal where you activated the Miniforge environment.
    Lines starting with `#` are comments and can be ignored.

    ```bash
    # Make sure your base environment is up-to-date.
    mamba update --all
    # Make a new environment for OpenMM, installing all the software, which takes some minutes.
    # The mamba create command is a single long line,
    # too long to fit on screen, so it is usually wrapped.
    # Make sure you copy it completely as a single line.
    mamba create -n famd python git numpy pandas scipy matplotlib ipympl jupyterlab rdkit openbabel openmm mdtraj nglview pdbfixer parmed stacie openff-toolkit
    # Activate the OpenMM environment
    mamba activate famd
    ```

    The `mamba update` and `mamba create` commands show the list of packages they will install or update and ask for confirmation.
    Check this list before approving it by typing `y` and pressing `Enter`.

    If you want GPU acceleration with CUDA, you only need to install the NVIDIA driver for your GPU,
    which can be downloaded from the [NVIDIA website](https://www.nvidia.com/Download/index.aspx) if needed.
    On Linux, the CUDA-enabled build of OpenMM is installed by default, with the CUDA libraries it needs,
    so no separate CUDA toolkit is needed.
    Install the driver before creating the environment, so that Mamba can pick an OpenMM build that is compatible with it.
    After the test in the next step, `CUDA` should appear in the list of available platforms.

1. Test your OpenMM installation with the following terminal command:

    ```bash
    python -m openmm.testInstallation
    ```

    You should see the following output (or something similar):

    ```
    OpenMM Version: 8.6.1
    Git Revision: b399af4725573963b46d6c1083fdcf7a37615857

    There are 2 Platforms available:

    1 Reference - Successfully computed forces
    2 CPU - Successfully computed forces

    Median difference in forces between platforms:

    Reference vs. CPU: 6.27834e-06

    All differences are within tolerance.
    ```

1. Now is a good time to familiarize yourself with the concept of a Jupyter Notebook.

    - If you want to use Jupyter Lab, the following links provide easy-to-follow guides, which will get you up to speed:

        - https://jupyterlab.readthedocs.io/en/stable/user/interface.html
        - https://jupyterlab.readthedocs.io/en/stable/user/notebook.html

      You can start Jupyter Lab on your own computer, e.g., by entering `jupyter lab` in the virtual terminal.

    - If you want to use VSCode, the following links provide easy-to-follow guides, which will get you up to speed:

        - https://code.visualstudio.com/
        - https://code.visualstudio.com/docs/python/jupyter-support

    Create a new Python 3 notebook in either Jupyter Lab or VSCode.
    Enter the following two lines in the first code cell and execute it by clicking on the play button in the toolbar (or typing Shift+Enter):

    ```python
    import openmm.testInstallation
    openmm.testInstallation.main()
    ```

    In VSCode, you will have to select the `famd` environment as the Python 3 kernel for the notebook.
    This should show the same output as in the previous step.

1. Install VMD, which will be used for showing some good visualization practices.
   Go to [the VMD download page](https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=VMD) and follow the instructions.

## Workaround for NGLview 4.0.1 bug

The latest version of NGLview, 4.0.1, which is also the one on conda-forge, installed with the instructions above,
has a severe bug that has not been fixed yet at the time of writing this documentation:
https://github.com/nglviewer/nglview/issues/1172

The workaround is to modify one file inside the `famd` Conda environment:
`~/miniforge3/envs/famd/lib/python3.14/site-packages/nglview/_frontend.py`.

It normally contains:

```python
__frontend_version__ = '4.0'
```

Change this to:

```python
__frontend_version__ = '3.1.5'
```

Instead of editing the file manually, you can also activate the `famd` environment and run:

```bash
sed -i.bak "s/^__frontend_version__ = .*/__frontend_version__ = '3.1.5'/" "${CONDA_PREFIX}"/lib/python*/site-packages/nglview/_frontend.py
```

(On macOS, this also works: the `.bak` suffix makes the `-i` option portable between GNU and BSD `sed`.)

This workaround is inherently fragile:
it modifies the installed package in place,
so it is lost whenever you update NGLview or recreate the environment.
In that case, apply it again.
Once a fixed NGLview release is available on conda-forge,
update the package (`mamba update nglview`) and do not apply this workaround.

## Usage

To start any notebook from the tutorial, download [the ZIP file with the most recent notebooks](https://github.com/molmod/famd-course/archive/main.zip) and unzip this archive.

- If you work with Jupyter Lab,
  open any terminal emulator and activate the mamba base environment:

    ```bash
    m
    ```

    Then change the directory to where you unzipped the archive.
    Once you have the right *current directory* in your virtual terminal, enter the following commands:

    ```bash
    mamba activate famd
    jupyter lab
    ```

- If you use VSCode, open the folder where you extracted the ZIP file,
  and then open any notebook file in the explorer.
  You need to select the `famd` Python 3 kernel when asked.

## Direnv instead of alias

Instead of defining the alias `m` and manually running `m` and `mamba activate famd`,
you can also use [direnv](https://direnv.net/) to automatically activate the `famd` environment
whenever you enter the directory where you work on the tutorials (or any of its subdirectories).

Put the following in your `~/.bashrc` (or `~/.bash_profile`) file to enable direnv for Bash:

```bash
eval "$(direnv hook bash)"
```

For Zsh, put `eval "$(direnv hook zsh)"` in your `~/.zshrc` file instead.

Then, in the directory where you work on the tutorials, create a `.envrc` file with the following content:

```bash
layout anaconda famd ~/miniforge3/bin/conda
```

The last argument is the location of the `conda` executable,
which is needed because Miniforge is not in your `PATH` by default.
Finally, allow direnv to use this file by running the following command in the same directory:

```bash
direnv allow
```

## Docker-based environment

(The instructions below have not been updated yet after renaming the repository to `famd-course`.)

Docker is a virtualization tool (think of it as a virtual computer inside your physical computer or laptop) that helps with creating a pre-defined working environment.
The benefit of this method is that it does not require the lengthy installation steps above, and the whole process takes less than 10 minutes.
The downside is that you may find the container abstraction confusing, but it is worthwhile to learn how Docker works, as many modern software projects support this approach.

1. Install Docker or Podman on your machine.

    To use a Docker image, you must first install Docker Desktop on your computer.
    Go to the [Docker website](https://www.docker.com/products/docker-desktop/) and download the latest version compatible with your operating system, e.g., macOS.

    Docker Desktop is free to use for individuals, but if you are working in an enterprise environment, consider using [Podman](https://podman.io/docs/installation), which has a much more permissive license (Apache 2.0).

1. Download the container image and start a new container.

    From the repository, run the following command:

    ```bash
    ./run_container.sh docker
    ```

    N.B. Replace `docker` with `podman` if you installed Podman instead.
    Also, if you are using Podman in a Linux environment, you need to add the following lines to your `/etc/containers/registries.conf` file,
    otherwise Podman will not be able to locate the Docker image defined in the `run_container.sh` file.

    ```toml
    [registries.search]
    registries = ['docker.io']
    ```

    After you run the command, the script should download the container image (only the first time) and start a Jupyter Lab session from the container.

1. Copy the Jupyter Lab URL from the command-line output and paste it into the browser.

    Look for the line that starts with `http://127.0.0.1:8888/lab?token=`.
    Copy the entire line and paste it into the browser, and you should be able to access the Jupyter Lab server and get started on the tutorial.
