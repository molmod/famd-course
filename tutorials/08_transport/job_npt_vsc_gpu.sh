#!/usr/bin/env bash
#SBATCH --job-name=npt-naoac
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=5GB
#SBATCH --time=1:00:00

# The NpT notebook needs Packmol, MDTraj and NGLView, which are included in the PhyStack environment.
source ${VSC_SCRATCH}/phystack/venvs/3.14.2-GCCcore-15.2.0/activate.sh
# Suppress irrelevant warnings
export PYDEVD_DISABLE_FILE_VALIDATION=1
# Set the number of threads.
export OPENMM_CPU_THREADS=${SLURM_CPUS_PER_TASK}
# Use CUDA for GPUs
export OPENMM_DEFAULT_PLATFORM=CUDA
# Go to the directory where sbatch was called
cd ${SLURM_SUBMIT_DIR}

# Run the notebook and write the result to 01_npt_equilibration.html. (everything on a single line)
time jupyter nbconvert --to html --execute --allow-errors --ExecutePreprocessor.timeout=-1 01_npt_equilibration.ipynb
