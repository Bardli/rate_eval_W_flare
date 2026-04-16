#!/usr/bin/env python3
"""
Calculate Balanced Accuracy and AUROC for Multiple Diseases
Implementation based on the provided BalancedAccuracy metric logic
Focus metrics: Balanced Accuracy and AUROC
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import roc_auc_score


def calculate_balanced_accuracy_and_auroc(csv_file, disease_name):
    """
    Calculate balanced accuracy and AUROC from exam_probabilities.csv
    
    Balanced Accuracy = (Sensitivity + Specificity) / 2
    Sensitivity (Recall) = TP / (TP + FN)
    Specificity = TN / (TN + FP)
    AUROC = Area Under the Receiver Operating Characteristic Curve
    """
    print(f"\n📖 Reading file: {csv_file}")

    # Read the CSV file
    df = pd.read_csv(csv_file)

    print(f"📊 Number of rows: {len(df)}")
    
    # Extract predictions and true labels
    predictions = np.array(df['prediction'].values, dtype=np.int64)
    true_labels = np.array(df['true_label'].values, dtype=np.int64)
    
    # Get probabilities if available, otherwise use predictions
    if 'probability' in df.columns:
        probabilities = np.array(df['probability'].values, dtype=np.float64)
    else:
        probabilities = predictions.astype(np.float64)
    
    # Calculate confusion matrix elements
    tp = np.sum((predictions == 1) & (true_labels == 1))
    tn = np.sum((predictions == 0) & (true_labels == 0))
    fp = np.sum((predictions == 1) & (true_labels == 0))
    fn = np.sum((predictions == 0) & (true_labels == 1))
    
    # Calculate metrics
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
    balanced_acc = (sensitivity + specificity) / 2
    accuracy = (tp + tn) / len(df)
    
    # Calculate AUROC
    try:
        auroc = roc_auc_score(true_labels, probabilities)
    except:
        auroc = 0.0
    
    return {
        'disease': disease_name,
        'balanced_accuracy': balanced_acc,
        'auroc': auroc,
        'sensitivity': sensitivity,
        'specificity': specificity,
        'accuracy': accuracy,
        'tp': tp,
        'tn': tn,
        'fp': fp,
        'fn': fn,
        'total': len(df)
    }


def main():
    print("╔════════════════════════════════════════════════════════════════════════════════╗")
    print("║                  📊 Compute Balanced Accuracy and AUROC for 15 diseases       ║")
    print("╚════════════════════════════════════════════════════════════════════════════════╝")
    
    results_base_dir = Path("/home/baidu/scratch/Pillar_Eval/rate-evals/linear_probing/results")
    
    # Define diseases and their result directories
    diseases = [
        ('ascites', 'pillar0_ascites'),
        ('atherosclerosis', 'pillar0_atherosclerosis'),
        ('colorectal_cancer', 'pillar0_colorectal_cancer'),
        ('lymphadenopathy', 'pillar0_lymphadenopathy'),
        ('adrenal_hyperplasia', 'pillar0_adrenal_hyperplasia'),
        ('cholecystitis', 'pillar0_cholecystitis'),
        ('fatty_liver', 'pillar0_fatty_liver'),
        ('gallstone', 'pillar0_gallstone'),
        ('hydronephrosis', 'pillar0_hydronephrosis'),
        ('kidney_stone', 'pillar0_kidney_stone'),
        ('liver_calcifications', 'pillar0_liver_calcifications'),
        ('liver_cyst', 'pillar0_liver_cyst'),
        ('liver_lesion', 'pillar0_liver_lesion'),
        ('renal_cyst', 'pillar0_renal_cyst'),
        ('splenomegaly', 'pillar0_splenomegaly'),
    ]
    
    all_results = []
    
    for disease_name, result_dir_name in diseases:
        csv_file = results_base_dir / result_dir_name / "exam_probabilities.csv"
        
        if not csv_file.exists():
            print(f"\n❌ File does not exist: {csv_file}")
            continue

        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Processing disease: {disease_name.upper()}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        result = calculate_balanced_accuracy_and_auroc(str(csv_file), disease_name)
        all_results.append(result)
        
        print(f"✅ Results:")
        print(f"   🎯 Balanced Accuracy: {result['balanced_accuracy']:.4f}")
        print(f"   🎯 AUROC: {result['auroc']:.4f}")
        print(f"   📊 Sensitivity (Recall): {result['sensitivity']:.4f}")
        print(f"   📊 Specificity: {result['specificity']:.4f}")
        print(f"   📊 Accuracy: {result['accuracy']:.4f}")
        print(f"   📈 Confusion Matrix: TP={result['tp']}, TN={result['tn']}, FP={result['fp']}, FN={result['fn']}")
    
    # Print summary table
    print("\n" + "="*110)
    print("📋 Summary of Balanced Accuracy and AUROC for all diseases:")
    print("="*110)
    
    summary_df = pd.DataFrame(all_results)
    print(summary_df.to_string(index=False))
    
    # Save results to CSV
    output_file = results_base_dir / "balanced_accuracy_and_auroc_summary.csv"
    summary_df.to_csv(output_file, index=False)
    print(f"\n💾 Results saved to: {output_file}")
    
    # Print individual metrics - Focus on Balanced Accuracy and AUROC
    print("\n" + "="*110)
    print("📊 Key metric comparison (Balanced Accuracy and AUROC):")
    print("="*110)
    print(f"{'Disease':<25} {'Balanced Acc.':<18} {'AUROC':<15} {'Sensitivity':<15} {'Specificity':<15}")
    print("-"*110)
    for result in all_results:
        print(f"{result['disease']:<25} {result['balanced_accuracy']:<18.4f} {result['auroc']:<15.4f} {result['sensitivity']:<15.4f} {result['specificity']:<15.4f}")
    
    print("\n" + "="*110)
    avg_balanced_acc = summary_df['balanced_accuracy'].mean()
    avg_auroc = summary_df['auroc'].mean()
    print(f"🎯 Mean Balanced Accuracy: {avg_balanced_acc:.4f}")
    print(f"🎯 Mean AUROC: {avg_auroc:.4f}")
    print("="*110 + "\n")


if __name__ == '__main__':
    main()
