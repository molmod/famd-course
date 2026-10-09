#!/usr/bin/env bash
#SBATCH --job-name all-gpu-famd
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=10GB
#SBATCH --time=5:00:00

# It is assumed that you submit this job to Donphan.
source ${VSC_SCRATCH}/phystack/venvs/3.14.2-GCCcore-15.2.0/activate.sh
export OPENMM_CPU_THREADS=${SLURM_CPUS_PER_TASK}
export OPENMM_DEFAULT_PLATFORM=CUDA
python -m openmm.testInstallation
./runall.sh
