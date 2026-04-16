#!/usr/bin/env python3
"""
Command-line tool: Generate dataset configuration files and Manifest CSV
Features:
  - Generate train.json, valid.json, test.json from split.json
  - Generate a corrected manifest.csv (supports mapping folder names to standard IDs)
"""

import json
import os
import argparse
import pandas as pd
import re
from typing import List, Set
from pathlib import Path


def extract_sample_id(sample_path: str) -> str:
    """
    Extract the sample ID from a sample path/ID.
    Supports two formats:
    1. Simple format: amos_0001 (returned as-is)
    2. Path format: Dataset012_FLARE25_abdomen_disease_classify_Tr/.../amos_0001/ses-DEFAULT/amos_0001 (ID extracted)
    """
    # If it's already a simple amos ID, return directly
    if sample_path.startswith('amos_') and '/' not in sample_path:
        return sample_path

    # Otherwise, try to extract an amos_XXXX ID from the path
    match = re.search(r'(amos_\d+)(?:/|$)', sample_path)
    if match:
        return match.group(1)

    # If extraction fails, return the original path
    return sample_path


def generate_jsonl_lines(sample_names: List[str], nii_root: str) -> List[str]:
    """Generate sample lines in JSONL format."""
    lines = []
    for name in sample_names:
        # Extract the real sample ID
        sample_id = extract_sample_id(name)
        # Even though the cache takes priority, we still need to provide the NII path as a fallback
        nii_path = os.path.join(nii_root, f"{sample_id}.nii.gz")
        sample_obj = {
            "sample_name": sample_id,
            "nii_path": nii_path,
            "report_metadata": {}
        }
        lines.append(json.dumps(sample_obj, ensure_ascii=False))
    return lines


def save_file(path: str, content: str):
    """Save a file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generated file: {path}")


def match_folder_to_id(folder_name: str, valid_ids: Set[str]) -> str:
    """
    Try to map a cache folder name (e.g. amos_0004.1.0) back to a standard ID (e.g. amos_0004).
    valid_ids contains the standard IDs extracted from split.json (e.g. amos_0004).
    """
    # 1. Try exact match
    if folder_name in valid_ids:
        return folder_name

    # 2. Try match after stripping suffix (assuming suffix starts with .)
    # Example: amos_0004.1.0 -> amos_0004
    base_name = folder_name.split('.')[0]
    if base_name in valid_ids:
        return base_name

    # 3. Try extracting an amos ID from the folder name
    match = re.search(r'(amos_\d+)', folder_name)
    if match:
        amos_id = match.group(1)
        if amos_id in valid_ids:
            return amos_id

    # 4. If the ID itself contains . (uncommon), try a prefix match
    # Iterate over all valid IDs and see whether the folder name begins with it
    for vid in valid_ids:
        if folder_name.startswith(vid):
            # Ensure a clean match boundary (e.g. to prevent case_1 matching case_10)
            remainder = folder_name[len(vid):]
            if remainder == "" or remainder.startswith(".") or remainder.startswith("_"):
                return vid

    return None


def process_all(
    split_json_path: str,
    nii_root_dir: str,
    cache_root_dir: str,
    dataset_config_dir: str,
    cache_manifest_dir: str,
    verbose: bool = False
):
    """
    Main processing function.
    """
    print("🚀 Starting processing...")

    # --- Step 1: Read the split file to get standard IDs ---
    if not os.path.exists(split_json_path):
        print(f"❌ Split file not found: {split_json_path}")
        return False

    with open(split_json_path, "r", encoding="utf-8") as f:
        split_data = json.load(f)

    # Collect all valid IDs (used to validate cache folders)
    # Extract amos IDs from the paths in split.json
    train_paths = split_data.get("train", [])
    val_paths = split_data.get("val", [])

    train_ids = [extract_sample_id(p) for p in train_paths]
    val_ids = [extract_sample_id(p) for p in val_paths]
    all_valid_ids = set(train_ids + val_ids)

    print(f"📊 Total standard IDs: {len(all_valid_ids)} (Train: {len(train_ids)}, Val: {len(val_ids)})")
    if verbose and len(train_ids) > 0:
        print(f"   Example sample ID: {train_ids[0]}")

    # --- Step 2: Generate JSONL configuration files ---
    print("\n--- Generating Dataset JSONL ---")

    # train.json
    save_file(
        os.path.join(dataset_config_dir, "train.json"),
        "\n".join(generate_jsonl_lines(train_paths, nii_root_dir)) + "\n"
    )

    # valid.json & test.json (both use the val data)
    val_content = "\n".join(generate_jsonl_lines(val_paths, nii_root_dir)) + "\n"
    save_file(os.path.join(dataset_config_dir, "valid.json"), val_content)
    save_file(os.path.join(dataset_config_dir, "test.json"), val_content)

    # --- Step 3: Generate the corrected Manifest CSV ---
    print("\n--- Generating Cache Manifest CSV (with ID fix) ---")

    if not os.path.exists(cache_root_dir):
        print(f"❌ Cache directory does not exist: {cache_root_dir}")
        return False

    manifest_data = []
    matched_count = 0
    unmatched_count = 0
    unmatched_folders = []

    # Scan the cache directory
    cache_folders = sorted([d for d in os.listdir(cache_root_dir) if os.path.isdir(os.path.join(cache_root_dir, d))])

    for folder_name in cache_folders:
        folder_path = os.path.join(cache_root_dir, folder_name)

        # Try to match
        matched_id = match_folder_to_id(folder_name, all_valid_ids)

        if matched_id:
            # Successfully matched!
            # In the CSV, sample_name stores the standard ID (amos_0004)
            # image_cache_path stores the actual folder path (.../amos_0004.1.0)
            manifest_data.append({
                "sample_name": matched_id,
                "image_cache_path": os.path.abspath(folder_path)
            })
            matched_count += 1
        else:
            # Could not match - log a warning
            unmatched_count += 1
            unmatched_folders.append(folder_name)

    # Save the CSV
    output_csv_path = os.path.join(cache_manifest_dir, "manifest.csv")
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

    df = pd.DataFrame(manifest_data)
    if not df.empty:
        df = df.sort_values("sample_name")
        df.to_csv(output_csv_path, index=False)
        print(f"✅ CSV generated: {output_csv_path}")
        print(f"   - Successfully matched samples: {matched_count}")
        if unmatched_count > 0:
            print(f"   ⚠️ Unmatched folders: {unmatched_count}")
            if verbose:
                print(f"   Unmatched folders:")
                for uf in unmatched_folders[:10]:  # show at most 10
                    print(f"     - {uf}")
                if len(unmatched_folders) > 10:
                    print(f"     ... and {len(unmatched_folders) - 10} more")

        # Preview
        print("\nCSV content preview (first 3 rows):")
        print(df.head(3).to_string())
        print("\n✅ Processing complete!")
        return True
    else:
        print("❌ Generation failed: no valid samples matched.")
        if unmatched_folders:
            print(f"\nDetected {unmatched_count} cache folders, but none could be matched:")
            for uf in unmatched_folders[:10]:
                print(f"   ⚠️ {uf}")
            if len(unmatched_folders) > 10:
                print(f"   ... and {len(unmatched_folders) - 10} more")
            print("\n💡 Possible reasons:")
            print("   1. IDs in split.json do not match the cache folder names")
            print("   2. The cache directory is empty or the path is wrong")
            print("   3. Use --verbose to view detailed information")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate dataset configuration files and Manifest CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default paths
  python make_split_json.py

  # Specify custom paths
  python make_split_json.py \\
    --split-json /path/to/split.json \\
    --nii-root /path/to/imagesTr \\
    --cache-root /path/to/cache \\
    --output-dir /path/to/output

  # Enable verbose output
  python make_split_json.py --verbose
        """
    )

    # Define default paths
    default_nii_root = "/home/baidu/scratch/File_transfer/abdomen_disease_classify/imagesTr"
    default_split_json = "/home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons/splits_final_ascites.json"
    default_cache_root = "/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify"
    default_output_dir = "/home/baidu/scratch/Pillar_Eval/rate-evals/output"

    parser.add_argument(
        "--split-json",
        type=str,
        default=default_split_json,
        help=f"Split JSON file path (default: {default_split_json})"
    )

    parser.add_argument(
        "--nii-root",
        type=str,
        default=default_nii_root,
        help=f"Raw NII image folder path (default: {default_nii_root})"
    )

    parser.add_argument(
        "--cache-root",
        type=str,
        default=default_cache_root,
        help=f"Cache data root directory (default: {default_cache_root})"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=default_output_dir,
        help=f"Output directory (default: {default_output_dir})"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Run the processing function
    success = process_all(
        split_json_path=args.split_json,
        nii_root_dir=args.nii_root,
        cache_root_dir=args.cache_root,
        dataset_config_dir=args.output_dir,
        cache_manifest_dir=args.output_dir,
        verbose=args.verbose
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
