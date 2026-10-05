#!/bin/bash
#SBATCH --job-name=openmm-hpc-cpu
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=5GB
#SBATCH --time=5:00:00

# Setup our OpenMM environment.
# You have to set MSBS_ROOT correctly for your system.
MSBS_ROOT=${VSC_DATA}
eval "$(${MSBS_ROOT}/mambaforge/bin/conda shell.bash hook)"
conda activate openmm
# Set the number of threads.
export OPENMM_CPU_THREADS=${SLURM_CPUS_PER_TASK}
# Go to the directory where sbatch was called
cd ${SLURM_SUBMIT_DIR}

# Run the notebook. (everything on a single line)
time jupyter nbconvert --to notebook --execute --allow-errors --ExecutePreprocessor.timeout=-1 01_noninteractive_notebook_on_hpc.ipynb
