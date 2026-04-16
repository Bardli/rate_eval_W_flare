# Dataset Processing Pipeline

## Directory Structure

```
rate-evals/
└── split_jsons/                        # 📥 Input & 🐍 Scripts & 📤 Output (all-in-one directory)
    ├── splits_final_ascites.json       # Split JSON file
    ├── splits_final_atherosclerosis.json
    ├── splits_final_colorectal_cancer.json
    ├── splits_final_lymphadenopathy.json
    ├── make_split_json.py              # Core processing script
    ├── make_split_json.ipynb
    ├── process_diseases.sh             # Batch processing script
    └── output/                         # Processing results
        ├── ascites/
        │   ├── train.json
        │   ├── valid.json
        │   ├── test.json
        │   └── manifest.csv
        ├── atherosclerosis/
        ├── colorectal_cancer/
        └── lymphadenopathy/
```

## Quick Start

### 1. Single disease processing

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons

# Process the ascites dataset (using a simple relative path)
python make_split_json.py --split-json splits_final_ascites.json

# Or specify the output directory
python make_split_json.py --split-json splits_final_atherosclerosis.json --output-dir output/atherosclerosis
```

### 2. Batch processing of all diseases

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
bash process_diseases.sh
```

This will automatically process all 4 diseases and output to the `output/` directory.

## Command-line Arguments

### make_split_json.py

```
--split-json SPLIT_JSON
  Split JSON file path
  Default: split_jsons/splits_final_ascites.json

--nii-root NII_ROOT
  Raw NII image folder path
  Default: /home/baidu/scratch/File_transfer/abdomen_disease_classify/imagesTr

--cache-root CACHE_ROOT
  Cache data root directory
  Default: /home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify

--output-dir OUTPUT_DIR
  Output directory
  Default: output/

-v, --verbose
  Enable verbose output
```

## Output File Descriptions

### train.json / valid.json / test.json

JSONL format (one JSON object per line):

```json
{"sample_name": "amos_0001", "nii_path": "/path/to/amos_0001.nii.gz", "report_metadata": {}}
{"sample_name": "amos_0004", "nii_path": "/path/to/amos_0004.nii.gz", "report_metadata": {}}
```

### manifest.csv

CSV format with two columns:

```csv
sample_name,image_cache_path
amos_0001,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0001.1.0
amos_0004,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0004.1.0
```

## Data Statistics

### Processed Diseases

| Disease | Split JSON | Train | Val | Total | Output |
|---------|-----------|-------|-----|-------|--------|
| ascites | split_jsons/splits_final_ascites.json | 1107 | 68 | 1175 | output/ascites/ |
| atherosclerosis | split_jsons/splits_final_atherosclerosis.json | 1107 | 52 | 1159 | output/atherosclerosis/ |
| colorectal_cancer | split_jsons/splits_final_colorectal_cancer.json | 1107 | 52 | 1159 | output/colorectal_cancer/ |
| lymphadenopathy | split_jsons/splits_final_lymphadenopathy.json | 1107 | 72 | 1179 | output/lymphadenopathy/ |

## Technical Details

### ID Extraction and Matching

**Problem**:
- Sample paths in split.json have a complex format: `Dataset012_FLARE25_abdomen_disease_classify_Tr/.../amos_0001/ses-DEFAULT/amos_0001`
- Cache folder format: `amos_0001.1.0`

**Solution**:
1. Use a regular expression to extract the `amos_XXXX` ID from split.json paths
2. Multi-level matching strategy: exact match → suffix stripping → regex extraction → prefix match
3. Generate manifest.csv to map cache folders to sample IDs

### Error Handling

- Unmatched folders are counted and reported
- Use the `--verbose` flag for detailed information
- The script continues processing and does not abort when some folders cannot be matched

## Usage Examples

### Example 1: Process a single disease

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
python make_split_json.py --split-json splits_final_ascites.json --verbose
```

### Example 2: Process all diseases

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
bash process_diseases.sh
```

### Example 3: Specify an output directory

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
python make_split_json.py \
  --split-json splits_final_colorectal_cancer.json \
  --output-dir output/colorectal_cancer
```

## Troubleshooting

### Issue: File not found
- Check whether the `split_jsons/` directory contains the corresponding split JSON file
- Confirm that the `NII_ROOT_DIR` and `CACHE_ROOT_DIR` paths are correct

### Issue: Low match rate
- Use `--verbose` to see which folders were not matched
- Check whether the ID format in split.json and the cache folder names are consistent

### Issue: Permission error
- Ensure you have write permissions for the `output/` directory
- Check read permissions on the source files

## Related Files

- `make_split_json.py` - Python processing script
- `process_diseases.sh` - Bash batch processing script
- `PROCESSING_SUMMARY.md` - Detailed processing summary

## Change Log

- 2025-12-09: Full directory consolidation; scripts and outputs both placed under the `split_jsons/` directory
- 2025-12-09: Restored split JSON files to the simple ID format (amos_0001 instead of full paths)
- 2025-12-09: Improved ID extraction and matching logic to support both formats
