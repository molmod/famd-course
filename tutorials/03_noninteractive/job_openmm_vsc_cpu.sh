#!/bin/bash
#SBATCH --job-name=openmm-vsc-cpu
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=5GB
#SBATCH --time=5:00:00

# Setup an OpenMM environment with CUDA support
ml load OpenMM/8.0.0-foss-2023a JupyterLab/4.0.5-GCCcore-12.3.0

# Suppress irrelevant warnings
export PYDEVD_DISABLE_FILE_VALIDATION=1
# Set the number of threads.
export OPENMM_CPU_THREADS=${SLURM_CPUS_PER_TASK}
# Go to the directory where sbatch was called
cd ${SLURM_SUBMIT_DIR}

# Run the notebook. (everything on a single line)
time jupyter nbconvert --to notebook --execute --allow-errors --ExecutePreprocessor.timeout=-1 01_noninteractive_notebook_on_hpc.ipynb
