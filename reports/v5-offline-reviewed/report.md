# v5 已有预测离线复评

Retrospective scorer-only reassessment; predictions and gold unchanged. Identical seven development exclusions are supplementary post-hoc analysis. Not a new clean-training result or final-test result.

| 模型 | 原64条 micro / macro | 修复评分64条 micro / macro | 排除7条问题标签后57条 micro / macro |
|---|---|---|---|
| base | 39.06% / 44.41% | 45.31% / 64.41% | 50.88% / 71.65% |
| checkpoint-33 | 60.94% / 44.41% | 67.19% / 64.41% | 73.68% / 72.22% |
| checkpoint-66 | 64.06% / 57.67% | 70.31% / 77.67% | 77.19% / 85.52% |

共 12 个逐模型判定变化，详见 changed_judgments.jsonl。完整 JSON 同时报告 raw/postprocessed、组指标、格式合规、解析覆盖及未验证数。

cp99 仅保留历史汇总，没有逐条预测，故不伪造新评分。开发集仅4组且分布偏斜；补充排除不能消除所有标签/评分限制。清洗后的训练数据尚未训练，以上涨分只来自评分修复。
