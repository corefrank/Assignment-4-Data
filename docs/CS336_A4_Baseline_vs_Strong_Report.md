# CS336 A4 — Common Crawl WET 数据清洗：Baseline vs Strong

## 1. 实验范围及数据来源

- 数据来源：Stanford CS336 A4 的真实 Common Crawl 示例 WET 文件，路径 `local-shared-data/CC/example.warc.wet.gz`。
- 源文件 SHA-256（此前 inspect 报告）：`cc2a41fc255f9336debd4e3335e50ce5581943bf687616fd06f3ae1c2d90eb6b`。
- 数据规模：单个完整示例 WET，19,637 条原始记录；**不是** Stanford A4 正式的 2,500 WET 文件实验。
- 对照方法：同一 WET 文件、相同基本过滤与去重及 GPT-2 分词设置；Strong 增加通用结构质量规则。
- 实验所用质量分类器：`quality_filter_enabled=false`，未启用 FastText quality classifier。

## 2. 实测结果

| 指标 | Baseline | Strong |
|---|---:|---:|
| 原始 WET 记录 | 19,637 | 19,637 |
| 过滤后保留文档 | 5,190 | 4,567 |
| 过滤保留率 | 26.43% | 23.26% |
| 去重后最终文档 | 5,162 | 4,543 |
| 精确行去重前的文本行 | 780,683 | 631,926 |
| 精确行去重删除行 | 465,407 | 375,596 |
| 各自输入中的精确行删除率 | 59.62% | 59.44% |
| MinHash + LSH 删除文档 | 0 | 0 |
| GPT-2 训练 tokens | 6,058,325 | 4,578,498 |
| tokenizer | GPT-2 | GPT-2 |
| token dtype | uint16 | uint16 |
| EOS 个数 | 5,162 | 4,543 |
| 过滤耗时 | 31.010s | 29.355s |
| 去重耗时 | 84.463s | 64.063s |
| 分词耗时 | 1.904s | 1.527s |
| 三阶段耗时合计 | 117.377s | 94.945s |

Strong 对比 Baseline：
- 过滤后保留文档减少 **623** 篇；最终去重后文档减少 **619** 篇（约 **12.0%**）。
- 训练 tokens 减少 **1,479,827**（约 **24.4%**）。
- 各阶段耗时合计减少约 **19.1%**。两次是独立运行，耗时仅代表本次本地实验，不可外推至 2,500 WET 或所有硬件环境。

### Strong 阶段的拒绝原因（按过滤漏斗顺序统计）

| 规则 | 拒绝文档 |
|---|---:|
| Repetitive trigrams | 313 |
| Low lexical diversity | 205 |
| Too few alphabetic words | 107 |
| Navigation heavy | 1 |
| **Strong 阶段合计** | **626** |

注意：Strong 阶段删除 626 篇并不意味着与最终 Base/Strong 文档差恰好 626；部分被 Strong 拒绝的文档在 Baseline 下还会被后续有害内容分类器拒绝。各阶段拒绝数是顺序漏斗统计，而非独立特征出现率。

## 3. 观察与分析

1. 两个配置都能完成 WET → 语言/质量规则与有害内容过滤 → PII masking → exact-line 去重 → MinHash/LSH → GPT-2 Tokenization 的端到端处理。
2. 精确行去重删除了约 59% 的输入文本行，说明网页正文里仍有大量跨文档重复的模板、导航和其他行级文本；这是**文本行比例**，不是删除了 59% 的文档。
3. 在此次数据与 `jaccard_threshold=0.8` 下，MinHash/LSH 没有进一步删除文档。单独把 `num_bands` 从 10 改为 20 仍删除 0 篇，并不能证明算法失效。
4. Strong 规则主要删除重复 trigram、词汇多样性低和字母词不足的内容；它减少了数据规模，但**尚不能证明** Paloma C4 100 验证损失更好。
5. 先前 Baseline 已通过 Stanford `cs336_basics.data.get_batch()` 的 CPU 格式检查（`x`/`y` 均为 `[2,512]`）。Strong 报告显示 uint16、EOS 与文档数一致；仍建议对 Strong 的 `train.bin` 单独完成同样的读取检查。

## 4. 人工审计

已人工审阅 Baseline 随机抽取的 5 篇保留和 5 篇拒绝样本：发现部分保留样本含法律公司宣传、导航和商品目录，另外存在较完整的新闻与科普文章；多数拒绝样本为非英语文本。基于这些观察提出 Strong 文本结构过滤假设。**尚未完成 Strong 独有删除样本的人工抽查**，不能断言其误删率或质量提升。

## 5. 复现命令

```bash
# Baseline：同一个完整真实示例 WET 文件
uv run python scripts/run_local_a4.py \
  local-shared-data/CC/example.warc.wet.gz \
  --work-dir data/a4_full_example

# Strong：只增加结构质量过滤；应使用一个新的输出目录
uv run python scripts/run_local_a4.py \
  local-shared-data/CC/example.warc.wet.gz \
  --work-dir data/a4_full_strong \
  --strong-filter

# Strong 训练文件的 CPU 兼容性验证
uv run python scripts/inspect_a4_run.py \
  --work-dir data/a4_full_strong \
  --wet-path local-shared-data/CC/example.warc.wet.gz
```

## 6. 结果边界与后续工作

- **已完成**：基于真实示例 WET 的过滤、PII、精确行去重、MinHash/LSH、GPT-2 uint16/EOS 分词，以及 Baseline/Strong 的可复现统计对照。
- **尚未完成**：正式 Wikipedia 引用外链构造并校准的 FastText 质量分类器；2,500 WET 全量处理；8×B200、16,384 steps 模型训练；Paloma C4 100 最佳验证损失/曲线。不要声称完成这些工作。
- **轻量级最后验证**：对 Strong 运行 `inspect_a4_run.py`；从 Baseline 保留且 Strong 删除的真实文档中抽取 5 篇，检查是否存在误删并记录到项目 README。

数据来源与参考：Stanford CS336 Assignment 4 官方项目 `stanford-cs336/assignment4-data`；keepkeen 的 `cs336-assignment4-data` 工程实现与中文博客。报告中的量化结果取自本地 `data/a4_full_example/pipeline_report.json` 与 `data/a4_full_strong/pipeline_report.json`，不是官方或他人的 benchmark 成绩。
