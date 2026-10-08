#!/usr/bin/env bash
#SBATCH --job-name=openmm-vsc-gpu
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=5GB
#SBATCH --time=5:00:00

# Start from a clean environment, ignoring modules loaded when sbatch was called
module purge
# Setup an OpenMM environment with CUDA support
ml load OpenMM/8.5.2-foss-2026.1-CUDA-12.9.1
# Jupyter (nbconvert, ipykernel) to run the notebook
ml load jupyter-server/2.19.0-GCCcore-15.2.0

# Suppress irrelevant warnings
export PYDEVD_DISABLE_FILE_VALIDATION=1
# Set the number of threads.
export OPENMM_CPU_THREADS=${SLURM_CPUS_PER_TASK}
# Use CUDA for GPUs
export OPENMM_DEFAULT_PLATFORM=CUDA
# Go to the directory where sbatch was called
cd ${SLURM_SUBMIT_DIR}

# Run the notebook. (everything on a single line)
time jupyter nbconvert --to notebook --execute --allow-errors --ExecutePreprocessor.timeout=-1 01_noninteractive_notebook_on_hpc.ipynb
