#!/bin/bash

# ==========================================
# Batch processing script for multiple disease classifications
# Function: Generate train.json, valid.json, test.json and manifest.csv for the specified diseases
# ==========================================

# ==========================================
# Configuration section
# ==========================================

# Path configuration
NII_ROOT_DIR="/home/baidu/scratch/File_transfer/abdomen_disease_classify/imagesTr"
SPLIT_JSON_DIR="/home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons"
CACHE_ROOT_DIR="/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify"
OUTPUT_BASE_DIR="/home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons/output"

# Focus disease list
# DISEASES=("ascites" "atherosclerosis" "colorectal_cancer" "lymphadenopathy")
DISEASES=("adrenal_hyperplasia" "cholecystitis" "fatty_liver" "gallstone" "hydronephrosis" "kidney_stone" "liver_calcifications" "liver_cyst" "liver_lesion" "renal_cyst" "splenomegaly")
# Python script path
PYTHON_SCRIPT="$(dirname "$0")/make_split_json.py"

# ==========================================
# Colored output (for readability)
# ==========================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ==========================================
# Function definitions
# ==========================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_file_exists() {
    if [ ! -f "$1" ]; then
        log_error "File does not exist: $1"
        return 1
    fi
    return 0
}

check_dir_exists() {
    if [ ! -d "$1" ]; then
        log_error "Directory does not exist: $1"
        return 1
    fi
    return 0
}

process_disease() {
    local disease=$1
    local output_subdir="$OUTPUT_BASE_DIR/$disease"
    local split_json_file="$SPLIT_JSON_DIR/splits_final_${disease}.json"

    log_info "Processing disease: $disease"

    # Check split.json file
    if ! check_file_exists "$split_json_file"; then
        log_warn "Skipping $disease (split.json not found)"
        return 1
    fi

    # Create output directory
    mkdir -p "$output_subdir"
    log_info "Output directory: $output_subdir"

    # Invoke the Python script
    log_info "Executing processing script..."
    if python "$PYTHON_SCRIPT" \
        --split-json "$split_json_file" \
        --nii-root "$NII_ROOT_DIR" \
        --cache-root "$CACHE_ROOT_DIR" \
        --output-dir "$output_subdir" \
        --verbose; then
        log_success "$disease processed successfully!"
        echo ""
        return 0
    else
        log_error "$disease processing failed"
        return 1
    fi
}

# ==========================================
# Main program
# ==========================================

main() {
    log_info "=========================================="
    log_info "Starting batch processing of disease classification datasets"
    log_info "=========================================="
    echo ""

    # Check prerequisites
    log_info "Checking prerequisites..."

    if ! check_dir_exists "$NII_ROOT_DIR"; then
        log_error "NII directory does not exist"
        exit 1
    fi

    if ! check_dir_exists "$SPLIT_JSON_DIR"; then
        log_error "Split JSON directory does not exist"
        exit 1
    fi

    if ! check_dir_exists "$CACHE_ROOT_DIR"; then
        log_error "Cache root directory does not exist"
        exit 1
    fi

    if ! check_file_exists "$PYTHON_SCRIPT"; then
        log_error "Python script does not exist: $PYTHON_SCRIPT"
        exit 1
    fi

    log_success "Prerequisite checks passed"
    echo ""

    # Process all diseases
    success_count=0
    failed_count=0

    for disease in "${DISEASES[@]}"; do
        if process_disease "$disease"; then
            ((success_count++))
        else
            ((failed_count++))
        fi
    done

    # Summary
    echo ""
    log_info "=========================================="
    log_info "Processing complete"
    log_info "=========================================="
    log_success "Successfully processed: $success_count disease(s)"

    if [ $failed_count -gt 0 ]; then
        log_warn "Failed: $failed_count disease(s)"
    fi

    # Display output file locations
    echo ""
    log_info "Output file locations:"
    for disease in "${DISEASES[@]}"; do
        if [ -d "$OUTPUT_BASE_DIR/$disease" ]; then
            echo "  $OUTPUT_BASE_DIR/$disease/"
            echo "    ├── train.json"
            echo "    ├── valid.json"
            echo "    ├── test.json"
            echo "    └── manifest.csv"
        fi
    done

    if [ $failed_count -eq 0 ]; then
        log_success "All diseases processed successfully!"
        exit 0
    else
        log_warn "Some diseases failed to process, please review the error messages above"
        exit 1
    fi
}

# ==========================================
# Run main program
# ==========================================

main "$@"
