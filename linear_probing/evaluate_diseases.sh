#!/bin/bash

# Linear Probing Evaluation Script
# Evaluate embeddings for multiple diseases using rate-evaluate

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/baidu/scratch/Pillar_Eval/rate-evals"
LINEAR_PROBING_DIR="$PROJECT_ROOT/linear_probing"
EMBEDDINGS_BASE_DIR="$PROJECT_ROOT/embeddings"
RESULTS_BASE_DIR="$LINEAR_PROBING_DIR/results"

source /home/baidu/scratch/Pillar_Eval/rave/.venv/bin/activate
# Create results directory
mkdir -p "$RESULTS_BASE_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}║              🔍 Starting Linear Probing evaluation for 15 diseases            ║${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Array of diseases with their configurations
declare -A DISEASES
DISEASES[ascites]="amos_ascites"
DISEASES[atherosclerosis]="amos_atherosclerosis"
DISEASES[colorectal_cancer]="amos_colorectal_cancer"
DISEASES[lymphadenopathy]="amos_lymphadenopathy"
DISEASES[adrenal_hyperplasia]="amos_adrenal_hyperplasia"
DISEASES[cholecystitis]="amos_cholecystitis"
DISEASES[fatty_liver]="amos_fatty_liver"
DISEASES[gallstone]="amos_gallstone"
DISEASES[hydronephrosis]="amos_hydronephrosis"
DISEASES[kidney_stone]="amos_kidney_stone"
DISEASES[liver_calcifications]="amos_liver_calcifications"
DISEASES[liver_cyst]="amos_liver_cyst"
DISEASES[liver_lesion]="amos_liver_lesion"
DISEASES[renal_cyst]="amos_renal_cyst"
DISEASES[splenomegaly]="amos_splenomegaly"

# Counter for tracking progress
DISEASE_COUNT=${#DISEASES[@]}
CURRENT=0

for disease in "${!DISEASES[@]}"; do
  CURRENT=$((CURRENT + 1))
  
  dataset_name="${DISEASES[$disease]}"
  checkpoint_dir="$EMBEDDINGS_BASE_DIR/$disease"
  labels_json="$LINEAR_PROBING_DIR/labels_${disease}.json"
  output_dir="$RESULTS_BASE_DIR/pillar0_${disease}"
  
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}[${CURRENT}/${DISEASE_COUNT}]${NC} Evaluating disease: ${YELLOW}${disease}${NC}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo "📁 Checkpoint directory: $checkpoint_dir"
  echo "📁 Labels file: $labels_json"
  echo "📁 Output directory: $output_dir"
  echo ""
  
  # Check if embeddings directory exists
  if [ ! -d "$checkpoint_dir" ]; then
    echo -e "${RED}❌ Embeddings directory does not exist: $checkpoint_dir${NC}"
    echo -e "${YELLOW}⚠️  Skipping this disease${NC}\n"
    continue
  fi

  # Check if labels file exists
  if [ ! -f "$labels_json" ]; then
    echo -e "${RED}❌ Labels file does not exist: $labels_json${NC}"
    echo -e "${YELLOW}⚠️  Skipping this disease${NC}\n"
    continue
  fi
  
  # Create output directory
  mkdir -p "$output_dir"
  
  # Run the evaluation command
  echo -e "${BLUE}Executing command:${NC}"
  echo "uv run rate-evaluate \\"
  echo "  --checkpoint-dir ${checkpoint_dir} \\"
  echo "  --dataset-name ${dataset_name} \\"
  echo "  --labels-json ${labels_json} \\"
  echo "  --output-dir ${output_dir}"
  echo ""
  
  cd "$PROJECT_ROOT"
  
  uv run rate-evaluate \
    --checkpoint-dir ${checkpoint_dir} \
    --dataset-name ${dataset_name} \
    --labels-json ${labels_json} \
    --output-dir ${output_dir}
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ${disease} evaluation succeeded!${NC}"
  else
    echo -e "${RED}❌ ${disease} evaluation failed!${NC}"
  fi
  
  echo ""
done

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}║                  ✅ Linear Probing evaluation complete for all diseases!      ║${NC}"
echo -e "${BLUE}║                                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}📊 Evaluation results directory structure:${NC}"
echo "results/"
for disease in "${!DISEASES[@]}"; do
  echo "├── pillar0_${disease}/"
  echo "│   ├── metrics.json"
  echo "│   ├── results.json"
  echo "│   └── ..."
done
echo ""
echo -e "${YELLOW}💡 View evaluation results:${NC}"
echo "  ls -lh $RESULTS_BASE_DIR/"
echo ""
