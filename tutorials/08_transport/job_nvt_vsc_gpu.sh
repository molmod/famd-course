#!/usr/bin/env bash
#SBATCH --job-name=nvt-naoac
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=5GB
#SBATCH --time=6:00:00

# Use the PhyStack environment, as for the NpT notebook.
source ${VSC_SCRATCH}/phystack/venvs/3.14.2-GCCcore-15.2.0/activate.sh
# Suppress irrelevant warnings
export PYDEVD_DISABLE_FILE_VALIDATION=1
# Set the number of threads.
export OPENMM_CPU_THREADS=${SLURM_CPUS_PER_TASK}
# Use CUDA for GPUs
export OPENMM_DEFAULT_PLATFORM=CUDA
# Go to the directory where sbatch was called
cd ${SLURM_SUBMIT_DIR}

# Run the notebook. The executed copy is written to 02_nvt_production.nbconvert.ipynb.
# Follow the progress with: tail -f scalars_nvt.csv
time jupyter nbconvert --to notebook --execute --allow-errors --ExecutePreprocessor.timeout=-1 02_nvt_production.ipynb
