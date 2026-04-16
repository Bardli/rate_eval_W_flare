# Dataset Processing Pipeline

## 目录结构

```
rate-evals/
└── split_jsons/                        # 📥 输入 & 🐍 脚本 & 📤 输出（一体化目录）
    ├── splits_final_ascites.json       # Split JSON 文件
    ├── splits_final_atherosclerosis.json
    ├── splits_final_colorectal_cancer.json
    ├── splits_final_lymphadenopathy.json
    ├── make_split_json.py              # 核心处理脚本
    ├── make_split_json.ipynb
    ├── process_diseases.sh             # 批量处理脚本
    └── output/                         # 处理结果
        ├── ascites/
        │   ├── train.json
        │   ├── valid.json
        │   ├── test.json
        │   └── manifest.csv
        ├── atherosclerosis/
        ├── colorectal_cancer/
        └── lymphadenopathy/
```

## 快速开始

### 1. 单个疾病处理

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons

# 处理 ascites 数据集（使用简单相对路径）
python make_split_json.py --split-json splits_final_ascites.json

# 或指定输出目录
python make_split_json.py --split-json splits_final_atherosclerosis.json --output-dir output/atherosclerosis
```

### 2. 批量处理所有疾病

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
bash process_diseases.sh
```

这将自动处理所有 4 个疾病，输出到 `output/` 目录。

## 命令行参数

### make_split_json.py

```
--split-json SPLIT_JSON
  Split JSON 文件路径
  默认: split_jsons/splits_final_ascites.json

--nii-root NII_ROOT
  原始 NII 影像文件夹路径
  默认: /home/baidu/scratch/File_transfer/abdomen_disease_classify/imagesTr

--cache-root CACHE_ROOT
  缓存数据根目录
  默认: /home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify

--output-dir OUTPUT_DIR
  输出目录
  默认: output/

-v, --verbose
  启用详细输出
```

## 输出文件说明

### train.json / valid.json / test.json

JSONL 格式（每行一个 JSON 对象）：

```json
{"sample_name": "amos_0001", "nii_path": "/path/to/amos_0001.nii.gz", "report_metadata": {}}
{"sample_name": "amos_0004", "nii_path": "/path/to/amos_0004.nii.gz", "report_metadata": {}}
```

### manifest.csv

CSV 格式，包含两列：

```csv
sample_name,image_cache_path
amos_0001,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0001.1.0
amos_0004,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0004.1.0
```

## 数据统计

### 已处理的疾病

| 疾病 | Split JSON | 训练集 | 验证集 | 总样本 | 输出文件 |
|------|----------|--------|--------|--------|---------|
| ascites | split_jsons/splits_final_ascites.json | 1107 | 68 | 1175 | output/ascites/ |
| atherosclerosis | split_jsons/splits_final_atherosclerosis.json | 1107 | 52 | 1159 | output/atherosclerosis/ |
| colorectal_cancer | split_jsons/splits_final_colorectal_cancer.json | 1107 | 52 | 1159 | output/colorectal_cancer/ |
| lymphadenopathy | split_jsons/splits_final_lymphadenopathy.json | 1107 | 72 | 1179 | output/lymphadenopathy/ |

## 技术细节

### ID 提取和匹配

**问题**：
- split.json 中的样本路径格式复杂：`Dataset012_FLARE25_abdomen_disease_classify_Tr/.../amos_0001/ses-DEFAULT/amos_0001`
- 缓存文件夹格式：`amos_0001.1.0`

**解决方案**：
1. 从 split.json 路径中使用正则表达式提取 `amos_XXXX` 格式的 ID
2. 多级匹配策略：完全匹配 → 后缀去除 → 正则提取 → 前缀匹配
3. 生成 manifest.csv 用于建立缓存文件夹与样本 ID 的映射

### 错误处理

- 未匹配的文件夹会被统计报告
- 使用 `--verbose` 标志获取详细信息
- 脚本继续处理，不会因为部分文件夹无法匹配而中断

## 使用示例

### 示例 1：处理单个疾病

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
python make_split_json.py --split-json splits_final_ascites.json --verbose
```

### 示例 2：处理所有疾病

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
bash process_diseases.sh
```

### 示例 3：指定输出目录

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
python make_split_json.py \
  --split-json splits_final_colorectal_cancer.json \
  --output-dir output/colorectal_cancer
```

## 故障排除

### 问题：文件未找到
- 检查 split_jsons/ 目录是否包含相应的 split JSON 文件
- 确认 NII_ROOT_DIR 和 CACHE_ROOT_DIR 路径正确

### 问题：匹配率低
- 使用 `--verbose` 查看哪些文件夹未匹配
- 检查 split.json 和缓存文件夹的 ID 格式是否一致

### 问题：权限错误
- 确保对 output/ 目录有写入权限
- 检查源文件的读取权限

## 相关文件

- `make_split_json.py` - Python 处理脚本
- `process_diseases.sh` - Bash 批量处理脚本
- `PROCESSING_SUMMARY.md` - 详细处理总结

## 更新历史

- 2025-12-09：完整目录整合，将脚本和输出都放入 `split_jsons/` 目录
- 2025-12-09：恢复 split JSON 文件为简单 ID 格式（amos_0001 而非完整路径）
- 2025-12-09：改进 ID 提取和匹配逻辑，支持两种格式
