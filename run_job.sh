#!/bin/bash
#SBATCH --account=bdgi-delta-gpu
#SBATCH --partition=gpuA40x4
#SBATCH --nodes=1
#SBATCH --gpus=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH --time=4:00:00
#SBATCH --job-name=hy_qoz_5e-3
#SBATCH --output=hy_qoz_5e-3.out
#SBATCH --error=hy_qoz_5e-3.err

# 加载conda环境
source ~/.bashrc   # 确保能找到 conda
cd ~/ASTZ
conda activate /u/zjian1/ASTZ/ASTZ_env

# 运行程序
# python3 starter.py
python3 test_transformer_ppl.py