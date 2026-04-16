#!/usr/bin/env python3
"""
Convert disease labels to Linear Probing format
Convert simple labels {amos_XXXX: 0/1} to nested format with qa_results
"""

import json
import sys
from pathlib import Path

def convert_to_qa_format(input_labels):
    """
    Convert simple label format to QA format
    
    Input: {"amos_0001": 0, "amos_0013": 1, ...}
    Output: {
        "amos_0001": {
            "qa_results": {
                "default": [{"Has Abnormality?": 0}]
            }
        },
        "amos_0013": {
            "qa_results": {
                "default": [{"Has Abnormality?": 1}]
            }
        }
    }
    """
    qa_format = {}
    
    for sample_id, label in input_labels.items():
        qa_format[sample_id] = {
            "qa_results": {
                "default": [
                    {
                        "Has Abnormality?": label
                    }
                ]
            }
        }
    
    return qa_format

def process_disease_labels(disease_name, input_file, output_file):
    """
    Process labels for a specific disease
    """
    print(f"\n📖 Reading file: {input_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_labels = json.load(f)
    except FileNotFoundError:
        print(f"❌ File does not exist: {input_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error: {e}")
        return False

    print(f"📊 Original data: {len(input_labels)} records")

    # Convert format
    qa_labels = convert_to_qa_format(input_labels)

    # Sort by ID
    qa_labels_sorted = dict(sorted(qa_labels.items(), key=lambda x: (
        int(x[0].split('_')[1]) if len(x[0].split('_')) > 1 else 0
    )))

    print(f"✅ Conversion complete: {len(qa_labels_sorted)} records")

    # Write to output file
    print(f"💾 Writing file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(qa_labels_sorted, f, indent=2, ensure_ascii=False)
    
    return True

def main():
    """
    Main function to process all disease labels
    """
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║                  🔄 Converting label format to Linear Probing format          ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝\n")

    # Define diseases and their corresponding input/output files
    diseases = [
        {
            'name': 'ascites',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_ascites.json',
            'output': 'labels_ascites.json'
        },
        {
            'name': 'atherosclerosis',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_atherosclerosis.json',
            'output': 'labels_atherosclerosis.json'
        },
        {
            'name': 'colorectal_cancer',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_colorectal_cancer.json',
            'output': 'labels_colorectal_cancer.json'
        },
        {
            'name': 'lymphadenopathy',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_lymphadenopathy.json',
            'output': 'labels_lymphadenopathy.json'
        },
        {
            'name': 'adrenal_hyperplasia',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_adrenal_hyperplasia.json',
            'output': 'labels_adrenal_hyperplasia.json'
        },
        {
            'name': 'cholecystitis',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_cholecystitis.json',
            'output': 'labels_cholecystitis.json'
        },
        {
            'name': 'fatty_liver',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_fatty_liver.json',
            'output': 'labels_fatty_liver.json'
        },
        {
            'name': 'gallstone',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_gallstone.json',
            'output': 'labels_gallstone.json'
        },
        {
            'name': 'hydronephrosis',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_hydronephrosis.json',
            'output': 'labels_hydronephrosis.json'
        },
        {
            'name': 'kidney_stone',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_kidney_stone.json',
            'output': 'labels_kidney_stone.json'
        },
        {
            'name': 'liver_calcifications',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_liver_calcifications.json',
            'output': 'labels_liver_calcifications.json'
        },
        {
            'name': 'liver_cyst',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_liver_cyst.json',
            'output': 'labels_liver_cyst.json'
        },
        {
            'name': 'liver_lesion',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_liver_lesion.json',
            'output': 'labels_liver_lesion.json'
        },
        {
            'name': 'renal_cyst',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_renal_cyst.json',
            'output': 'labels_renal_cyst.json'
        },
        {
            'name': 'splenomegaly',
            'input': '/home/baidu/scratch/File_transfer/abdomen_disease_classify/cls_labels/labelsTr_splenomegaly.json',
            'output': 'labels_splenomegaly.json'
        }
    ]
    
    # Get the directory of this script (linear_probing folder)
    script_dir = Path(__file__).parent

    success_count = 0

    for disease in diseases:
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Processing disease: {disease['name'].upper()}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        output_path = script_dir / disease['output']
        
        if process_disease_labels(disease['name'], disease['input'], str(output_path)):
            success_count += 1
    
    print("\n╔════════════════════════════════════════════════════════════════════════════════╗")
    print(f"║                    ✅ Processing complete: {success_count}/15 files                 ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝\n")

    print("📁 Generated files:")
    print(f"   {script_dir}/")
    for disease in diseases:
        output_path = script_dir / disease['output']
        if output_path.exists():
            file_size = output_path.stat().st_size / 1024  # KB
            print(f"   ├── {disease['output']} ({file_size:.1f} KB)")
    
    print("\n💡 File format description:")
    print("   {")
    print("     \"amos_0001\": {")
    print("       \"qa_results\": {")
    print("         \"default\": [{")
    print("           \"Has Abnormality?\": 0")
    print("         }]")
    print("       }")
    print("     }")
    print("   }")
    print()

if __name__ == '__main__':
    main()
