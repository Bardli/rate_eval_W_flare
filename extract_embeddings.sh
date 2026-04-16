#!/bin/bash
#SBATCH --account=def-jma-ab
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=12
#SBATCH --mem=60G

#SBATCH --gpus-per-node=h100:1  # full 1xH100
##SBATCH --gpus=nvidia_h100_80gb_hbm3_3g.40gb:1  # part of 1xH100
##SBATCH --gpus=nvidia_h100_80gb_hbm3_1g.10gb:1
#SBATCH --time=1-0:0
#SBATCH --mail-user=bardli2001@gmail.com
#SBATCH --mail-type=ALL
#SBATCH --output=/scratch/baidu/slurm_logs/%x_%j.log
module load python/3.11
module load cuda/12.6
module load cmake/3.31.0
module load rust/1.91.0


# Extract embeddings for multiple diseases using Pillar0 model
# This script processes 4 diseases: ascites, atherosclerosis, colorectal_cancer, lymphadenopathy

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/baidu/scratch/Pillar_Eval/rate-evals"
MODEL_REPO_ID="/home/baidu/scratch/Pillar_Eval/Pillar0-AbdomenCT"
OUTPUT_BASE_DIR="$PROJECT_ROOT/embeddings"
BATCH_SIZE=5
CT_WINDOW_TYPE="all"
MODALITY="abdomen_ct"

source /home/baidu/scratch/Pillar_Eval/rave/.venv/bin/activate
# Array of diseases
# DISEASES=("ascites" "atherosclerosis" "colorectal_cancer" "lymphadenopathy")
DISEASES=("adrenal_hyperplasia" "cholecystitis" "fatty_liver" "gallstone" "hydronephrosis" "kidney_stone" "liver_calcifications" "liver_cyst" "liver_lesion" "renal_cyst" "splenomegaly")
# Create output directory
mkdir -p "$OUTPUT_BASE_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}║              🔧 开始提取11个疾病的Embedding特征                               ║${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Counter for tracking progress
DISEASE_COUNT=${#DISEASES[@]}
CURRENT=0

for disease in "${DISEASES[@]}"; do
  CURRENT=$((CURRENT + 1))
  
  OUTPUT_DIR="$OUTPUT_BASE_DIR/$disease"
  
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}[${CURRENT}/${DISEASE_COUNT}]${NC} 正在处理疾病: ${YELLOW}${disease}${NC}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo "📁 输出目录: $OUTPUT_DIR"
  echo ""
  
  mkdir -p "$OUTPUT_DIR"
  
  # Run the embedding extraction command
  echo -e "${BLUE}执行命令:${NC}"
  echo "uv run rate-extract \\"
  echo "  --model pillar0 \\"
  echo "  --dataset amos_${disease} \\"
  echo "  --all-splits \\"
  echo "  --batch-size ${BATCH_SIZE} \\"
  echo "  --output-dir ${OUTPUT_DIR} \\"
  echo "  --model-repo-id ${MODEL_REPO_ID} \\"
  echo "  --model-revision local \\"
  echo "  --ct-window-type ${CT_WINDOW_TYPE} \\"
  echo "  --modality ${MODALITY}"
  echo ""
  
  cd "$PROJECT_ROOT"
  
  uv run rate-extract \
    --model pillar0 \
    --dataset amos_${disease} \
    --all-splits \
    --batch-size ${BATCH_SIZE} \
    --output-dir ${OUTPUT_DIR} \
    --model-repo-id ${MODEL_REPO_ID} \
    --model-revision local \
    --ct-window-type ${CT_WINDOW_TYPE} \
    --modality ${MODALITY}
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ${disease} embedding 提取成功!${NC}"
  else
    echo -e "${RED}❌ ${disease} embedding 提取失败!${NC}"
  fi
  
  echo ""
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}║                    ✅ 所有疾病的 embedding 提取完成！                         ║${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 生成的 embedding 目录结构:${NC}"
echo "embeddings/"
for disease in "${DISEASES[@]}"; do
  echo "├── ${disease}/"
  echo "│   ├── train_embeddings/"
  echo "│   ├── valid_embeddings/"
  echo "│   └── test_embeddings/"
done
echo ""
