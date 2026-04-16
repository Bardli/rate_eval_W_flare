# Rate-evals Dataset Processing Tool

## 📁 Directory Structure Overview

```
rate-evals/
├── split_jsons/                        # 📥 Inputs & 🐍 Scripts & 📤 Outputs
│   ├── splits_final_ascites.json       # Split JSON file
│   ├── splits_final_atherosclerosis.json
│   ├── splits_final_colorectal_cancer.json
│   ├── splits_final_lymphadenopathy.json
│   ├── make_split_json.py              # Core processing script
│   ├── make_split_json.ipynb           # Jupyter Notebook version
│   ├── process_diseases.sh             # Batch processing script
│   └── output/                         # Processing results
│       ├── ascites/
│       ├── atherosclerosis/
│       ├── colorectal_cancer/
│       └── lymphadenopathy/
```

## 🎯 Features

This tool is used to:
1. Generate standard-format train/valid/test dataset configurations from split JSON files
2. Build a mapping between cache folders and sample IDs (manifest.csv)
3. Support intelligent ID extraction and a multi-level matching strategy
4. Batch-process datasets for multiple diseases

## 🚀 Quick Usage

### Method 1: Process a single disease

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons

# Process the ascites dataset
python make_split_json.py --split-json splits_final_ascites.json

# Or specify the output directory
python make_split_json.py \
  --split-json splits_final_colorectal_cancer.json \
  --output-dir output/colorectal_cancer
```

### Method 2: Batch process all diseases

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
bash process_diseases.sh
```

This processes all 4 diseases, writing results to the corresponding `output/` subdirectory.

## 📋 Available Diseases

| # | Disease | Split file | Data size |
|---|---------|-----------|-----------|
| 1 | ascites | split_jsons/splits_final_ascites.json | 1175 |
| 2 | atherosclerosis | split_jsons/splits_final_atherosclerosis.json | 1159 |
| 3 | colorectal_cancer | split_jsons/splits_final_colorectal_cancer.json | 1159 |
| 4 | lymphadenopathy | split_jsons/splits_final_lymphadenopathy.json | 1179 |

## 📖 Detailed Documentation

- **USAGE.md** - Detailed command-line arguments and examples
- **ORGANIZATION.md** - Directory structure and reorganization summary
- **PROCESSING_SUMMARY.md** - Processing details and technical notes

## 🔧 Command-line Arguments

### make_split_json.py

```
Options:
  --split-json SPLIT_JSON      Split JSON file path (required)
  --nii-root NII_ROOT          NII image folder path (optional, defaults to standard path)
  --cache-root CACHE_ROOT      Cache data root directory (optional, defaults to standard path)
  --output-dir OUTPUT_DIR      Output directory (optional, defaults to output/)
  -v, --verbose                Enable verbose output

Examples:
  # Simplest usage (with all defaults)
  python make_split_json.py --split-json split_jsons/splits_final_ascites.json

  # Enable verbose output
  python make_split_json.py --split-json split_jsons/splits_final_ascites.json --verbose

  # Custom output directory
  python make_split_json.py \
    --split-json split_jsons/splits_final_ascites.json \
    --output-dir /tmp/my_output
```

## 📊 Output File Descriptions

Each disease directory contains 4 files:

### 1. train.json
- **Format**: JSONL (one JSON object per line)
- **Contents**: Training sample configuration
- **Example**:
```json
{"sample_name": "amos_0001", "nii_path": "/path/to/amos_0001.nii.gz", "report_metadata": {}}
```

### 2. valid.json
- **Format**: JSONL
- **Contents**: Validation sample configuration
- **Row count**: Depends on the number of val samples in split.json

### 3. test.json
- **Format**: JSONL
- **Contents**: Test sample configuration (same as valid.json)

### 4. manifest.csv
- **Format**: CSV (2 columns)
- **Columns**: sample_name, image_cache_path
- **Purpose**: Maps sample IDs to cache folders
- **Example**:
```csv
sample_name,image_cache_path
amos_0001,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0001.1.0
amos_0004,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0004.1.0
```

## 🔍 Technical Details

### ID Extraction Mechanism

**Background**:
- Sample path format in split.json: `Dataset012_FLARE25_abdomen_disease_classify_Tr/.../amos_0001/ses-DEFAULT/amos_0001`
- Cache folder format: `amos_0001.1.0`
- These two formats need to be mapped to each other

**Solution**:
1. **Path parsing**: Use the regular expression `(amos_\d+)` to extract the standard ID from the complex path
2. **Multi-level matching**:
   - Level 1: Exact match
   - Level 2: Suffix-stripped match (`amos_0001.1.0` → `amos_0001`)
   - Level 3: Regex extraction match
   - Level 4: Prefix match (handles special formats)

### Error Handling

- **Unmatched folders**: Counted and reported without aborting
- **Detailed logs**: Use `--verbose` to see full match information
- **Error recovery**: Unmatched folders do not affect overall processing

## 💡 Usage Tips

### Workflow

1. **Check inputs**: Make sure `split_jsons/` contains the required split JSON files
2. **Run processing**: Run `python make_split_json.py` or `bash process_diseases.sh`
3. **Verify results**: Check that files under `output/` are complete
4. **Downstream processing**: Use manifest.csv and the JSON files for subsequent operations

### Performance

- **Single disease**: Processing time < 1 second
- **Batch processing**: 4 diseases < 10 seconds
- **Output size**: ~300K per disease

### Extending

It's easy to add more diseases:
1. Drop the new disease's split JSON into `split_jsons/`
2. Update the `DISEASES` array in `process_diseases.sh`
3. Run the script to generate outputs automatically

## 🐛 Troubleshooting

### Q1: File not found error
```
❌ Split file not found: /path/to/split.json
```
**Fix**: Check whether the file path is correct and that the split JSON file is in the `split_jsons/` directory

### Q2: Cache directory does not exist
```
❌ Cache directory does not exist: /path/to/cache
```
**Fix**: Confirm the `CACHE_ROOT_DIR` path is correct and that the directory exists

### Q3: Permission error
```
Permission denied
```
**Fix**: Check write permissions on the `output/` directory

### Q4: Low match rate
```
⚠️ Unmatched folders: 500
```
**Fix**:
- This is usually normal (unmatched folders may not belong to the disease)
- Use `--verbose` to see detailed information
- Check the ID format in split.json and the cache files

## 📝 Dependencies

- Python 3.6+
- pandas (for CSV and DataFrame handling)
- Standard library: json, os, re, argparse

## 🔄 Version History

### v1.2 (2025-12-09)
- ✨ Full directory consolidation: scripts and outputs both placed under split_jsons/
- ✨ Restored split JSON files to the simple ID format
- ✨ Simplified paths and usage

### v1.1 (2025-12-09)
- ✨ Reorganized directory structure
- ✨ Improved ID extraction and matching logic
- ✨ Added detailed documentation

### v1.0 (2025-12-09)
- Initial release: basic dataset processing functionality

## 📞 Support

If you run into issues, please consult:
1. USAGE.md - Detailed usage instructions
2. ORGANIZATION.md - Directory structure description
3. PROCESSING_SUMMARY.md - Processing details

## 📄 License

See LICENSE file for details.
