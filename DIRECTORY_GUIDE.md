# Rate-evals 数据集处理工具

## 📁 目录结构概览

```
rate-evals/
├── split_jsons/                        # 📥 输入 & 🐍 脚本 & 📤 输出
│   ├── splits_final_ascites.json       # Split JSON 文件
│   ├── splits_final_atherosclerosis.json
│   ├── splits_final_colorectal_cancer.json
│   ├── splits_final_lymphadenopathy.json
│   ├── make_split_json.py              # 核心处理脚本
│   ├── make_split_json.ipynb           # Jupyter Notebook 版本
│   ├── process_diseases.sh             # 批量处理脚本
│   └── output/                         # 处理结果
│       ├── ascites/
│       ├── atherosclerosis/
│       ├── colorectal_cancer/
│       └── lymphadenopathy/
```

## 🎯 功能

此工具用于：
1. 从 split JSON 文件生成标准格式的训练/验证/测试数据集配置
2. 建立缓存文件夹与样本 ID 的映射关系（manifest.csv）
3. 支持智能 ID 提取和多级匹配策略
4. 批量处理多个疾病的数据集

## 🚀 快速使用

### 方式 1：处理单个疾病

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons

# 处理 ascites 数据集
python make_split_json.py --split-json splits_final_ascites.json

# 或指定输出目录
python make_split_json.py \
  --split-json splits_final_colorectal_cancer.json \
  --output-dir output/colorectal_cancer
```

### 方式 2：批量处理所有疾病

```bash
cd /home/baidu/scratch/Pillar_Eval/rate-evals/split_jsons
bash process_diseases.sh
```

这将处理所有 4 个疾病，输出到相应的 `output/` 子目录。

## 📋 可用的疾病

| 编号 | 疾病名 | 英文 | Split 文件 | 数据量 |
|------|--------|------|-----------|--------|
| 1 | 腹水 | ascites | split_jsons/splits_final_ascites.json | 1175 |
| 2 | 动脉硬化 | atherosclerosis | split_jsons/splits_final_atherosclerosis.json | 1159 |
| 3 | 结直肠癌 | colorectal_cancer | split_jsons/splits_final_colorectal_cancer.json | 1159 |
| 4 | 淋巴结病 | lymphadenopathy | split_jsons/splits_final_lymphadenopathy.json | 1179 |

## 📖 详细文档

- **USAGE.md** - 命令行参数详解和使用示例
- **ORGANIZATION.md** - 目录结构和重组总结
- **PROCESSING_SUMMARY.md** - 处理过程和技术细节

## 🔧 命令行参数

### make_split_json.py

```
选项：
  --split-json SPLIT_JSON      Split JSON 文件路径（必需）
  --nii-root NII_ROOT          NII 影像文件夹路径（可选，默认为标准路径）
  --cache-root CACHE_ROOT      缓存数据根目录（可选，默认为标准路径）
  --output-dir OUTPUT_DIR      输出目录（可选，默认为 output/）
  -v, --verbose                启用详细输出

示例：
  # 最简单的用法（使用所有默认值）
  python make_split_json.py --split-json split_jsons/splits_final_ascites.json

  # 启用详细输出
  python make_split_json.py --split-json split_jsons/splits_final_ascites.json --verbose

  # 自定义输出目录
  python make_split_json.py \
    --split-json split_jsons/splits_final_ascites.json \
    --output-dir /tmp/my_output
```

## 📊 输出文件说明

每个疾病目录下包含 4 个文件：

### 1. train.json
- **格式**: JSONL（每行一个 JSON 对象）
- **内容**: 训练集样本配置
- **例子**:
```json
{"sample_name": "amos_0001", "nii_path": "/path/to/amos_0001.nii.gz", "report_metadata": {}}
```

### 2. valid.json
- **格式**: JSONL
- **内容**: 验证集样本配置
- **行数**: 取决于 split.json 中的 val 样本数

### 3. test.json
- **格式**: JSONL
- **内容**: 测试集样本配置（与 valid.json 相同）

### 4. manifest.csv
- **格式**: CSV（2 列）
- **列**: sample_name, image_cache_path
- **用途**: 映射样本 ID 到缓存文件夹
- **例子**:
```csv
sample_name,image_cache_path
amos_0001,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0001.1.0
amos_0004,/home/baidu/scratch/Pillar_Eval/RAVE_preprocessed/abdomen_disease_classify/amos_0004.1.0
```

## 🔍 技术细节

### ID 提取机制

**问题背景**：
- split.json 中的样本路径格式：`Dataset012_FLARE25_abdomen_disease_classify_Tr/.../amos_0001/ses-DEFAULT/amos_0001`
- 缓存文件夹格式：`amos_0001.1.0`
- 这两种格式的 ID 需要建立映射关系

**解决方案**：
1. **路径解析**: 使用正则表达式 `(amos_\d+)` 从复杂路径中提取标准 ID
2. **多级匹配**:
   - 第 1 级：完全匹配
   - 第 2 级：后缀去除匹配（`amos_0001.1.0` → `amos_0001`）
   - 第 3 级：正则提取匹配
   - 第 4 级：前缀匹配（处理特殊格式）

### 误差处理

- **未匹配的文件夹**: 统计报告但不中断处理
- **详细日志**: 使用 `--verbose` 查看完整匹配信息
- **错误恢复**: 部分文件夹未匹配不影响总体处理

## 💡 使用建议

### 工作流程

1. **检查输入**：确保 split_jsons/ 包含所需的 split JSON 文件
2. **处理数据**：运行 `python make_split_json.py` 或 `bash process_diseases.sh`
3. **验证结果**：检查 output/ 目录下的文件是否完整
4. **下游处理**：使用 manifest.csv 和 JSON 文件进行后续操作

### 性能优化

- **单个处理**: 处理速度 < 1 秒
- **批量处理**: 4 个疾病 < 10 秒
- **输出大小**: 每个疾病约 300K

### 扩展应用

可以轻松扩展处理其他疾病：
1. 将新疾病的 split JSON 放入 `split_jsons/`
2. 更新 `process_diseases.sh` 的 DISEASES 数组
3. 运行脚本自动生成输出

## 🐛 故障排除

### Q1: 文件未找到错误
```
❌ 找不到 Split 文件: /path/to/split.json
```
**解决**: 检查文件路径是否正确，split JSON 文件是否在 split_jsons/ 目录中

### Q2: 缓存目录不存在
```
❌ 缓存目录不存在: /path/to/cache
```
**解决**: 确认 CACHE_ROOT_DIR 路径正确，检查目录是否存在

### Q3: 权限错误
```
Permission denied
```
**解决**: 检查对 output/ 目录的写入权限

### Q4: 匹配率低
```
⚠️ 未匹配文件夹: 500 个
```
**解决**: 
- 这通常是正常的（未匹配的文件夹可能不属于该疾病）
- 使用 `--verbose` 查看详细信息
- 检查 split.json 和缓存文件的 ID 格式

## 📝 依赖项

- Python 3.6+
- pandas（用于处理 CSV 和 DataFrame）
- 标准库：json, os, re, argparse

## 🔄 版本历史

### v1.2 (2025-12-09)
- ✨ 完整目录整合：脚本和输出都放入 split_jsons/ 目录
- ✨ 恢复 split JSON 为简单 ID 格式
- ✨ 简化了路径和使用方式

### v1.1 (2025-12-09)
- ✨ 重新组织目录结构
- ✨ 改进 ID 提取和匹配逻辑
- ✨ 添加详细文档

### v1.0 (2025-12-09)
- 初始版本：基础数据集处理功能

## 📞 支持

如有问题，请检查：
1. USAGE.md - 详细使用说明
2. ORGANIZATION.md - 目录结构说明
3. PROCESSING_SUMMARY.md - 处理过程详情

## 📄 许可证

See LICENSE file for details.
