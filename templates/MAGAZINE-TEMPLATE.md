# 新领域弹匣模板

复制为新的 `library/<id>.vN.json`；先确定任务适用范围与来源，再生成目录（catalog）和宿主许可的绑定。不得覆盖已发布的版本。可参考 `demo/library/ab-test-review.v1.json` 与 `build_demo.py`。

## 基本信息

- magazine_id / version / domain：
- 适用任务与明确不适用的任务：
- 来源清单与固定快照：
- 来源真实性、独立性方面的限制：

## 逐条记录

- id / kind / title / topics：
- scope / purposes / permission：
- known_at / known_at_basis：
- embargo_oos：
- source.artifact / start_line / end_line：
- source.artifact_sha256 / excerpt_sha256：
- supersedes / required_context：

内容必须逐字可追溯。方法要写明适用条件；实验结果标为探索性；保留反例、失败记录、重要异议和控制性纠错。主张的适用范围不能被标题扩大。

目录只保存定位与哈希，不嵌入原文。装载器在通过许可检查之后才读取摘录。机器可读的字段格式见 `schemas/magazine.schema.json`。

## 宿主登记

由宿主明确工单、角色、用途、领域、可读文件、知识截止时间和字节预算。请求不能自行授权；没有来源的材料拒绝导入。复用现有格式时必须替换来源与许可，不要复制旧的授权来扩大新权限。

## 验证

选择可以实际核对的来源，先冻结错误案例与预期结果，再运行。报告里区分"装载规则测试"和"模型表现评估"；没做的项目明确写 `NOT_RUN`。通过后以新的目录快照发布，并保留原版本及其 SHA-256。
