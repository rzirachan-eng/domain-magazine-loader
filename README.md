# domain-magazine-loader · 领域弹匣

**A small, offline, standard-library-only Python module that loads domain knowledge for an AI agent *per task*, with every excerpt bound to a hashed source and every correction or objection travelling with the claim it affects.**

给 AI Agent 按任务装载领域知识的小型离线模块：只用 Python 标准库；每条知识都绑定到带哈希的原文摘录；被引用的结论一定连同它的纠错和异议一起出现。

> 本仓库里的实验、人物、数字全部是虚构的演示数据，只用来说明机制。

## 它解决什么问题

给 Agent 塞知识时，常见的毛病有四个：把已被更正的旧结论又塞回去、把还没公开或不该看的材料读进去、只给"赞成"不给"反对"、以及无法核对一句话到底出自哪里。弹匣的做法是把这些约束放进装载流程，而不是写在提示词里：

| 约束 | 做法 |
|---|---|
| 先过滤，后读文件 | 权限、用途、知识时点（`known_at`）、封存状态（`embargo_oos`）全部只看元数据；不合格的条目**连原文都不会被打开** |
| 原文可核对 | 每条记录只存"文件 + 起止行 + 两个 SHA-256"，不内嵌原文；装载时重新读取并核对哈希，逐字输出 |
| 纠错与异议不丢 | `supersedes` / `required_context` 构成原子闭包：选中旧结论必须同时带出纠错和主要异议，任一成员不可用就整组排除 |
| 预算按整包算 | 字节预算覆盖完整序列化结果（含元数据、排除记录、哈希）；超预算时整组丢弃，不会只丢异议留下结论 |
| 不能自己给自己授权 | 许可、预算、可读文件由宿主配置（带哈希绑定）决定，请求里多写一个字段就被拒绝 |
| 伪造和篡改 | 包带自哈希，渲染时还会用宿主重新装载一遍比对，"重算哈希的伪造包"也过不了 |
| 可卸载 | `unload_context` 后上下文字节与装载前完全一致 |
| 疑似凭据 | 来源文本匹配到私钥、`api_key=` 等模式时整条排除 |

## 快速试用

需要 Python 3.9+，无第三方依赖。

```bash
python cli.py --request demo/request.json --summary   # 摘要
python cli.py --request demo/request.json             # 完整包 + 带引用的渲染文本
python -m unittest discover -s tests                  # 65 个测试
python build_demo.py                                  # 重新生成演示数据（确定性，可与现有文件逐字节比对）
```

演示的结果：请求主题是 `uplift`、`conversion`、`method`，装载 4 条（旧结论、它的纠错、反对意见、方法说明）；另外 3 条被拦在读文件之前：

| 条目 | 原因 |
|---|---|
| `finance-memo` | `PERMISSION_DENIED`：该角色没有读取权限 |
| `q2-forecast` | `NOT_YET_KNOWN`：知识时点晚于请求截止时间 |
| `sealed-holdout` | `EMBARGO_OR_UNKNOWN`：封存数据 |

## 目录

```
domain_magazine.py   装载、过滤、核对、渲染、卸载（核心，标准库）
cli.py               本地命令行入口
build_demo.py        确定性生成演示数据
schemas/             弹匣与请求的 JSON Schema（运行时另有跨字段、来源、权限校验）
templates/           新领域弹匣的编写模板
tests/               单元测试
demo/                虚构的演示安装：sources/ library/ config/ bindings/ request.json
SPEC.md              格式、许可、时点、预算与回退契约
```

## 测试覆盖

`tests/` 里的负向用例占大头：越权的工单/角色/范围/用途/预算、未来知识、封存与未知状态、缺失或被改动的来源、伪造的包与渲染、路径穿越与软链接逃逸、纠错遗漏、预算不足、提示注入文本只当数据、疑似凭据，以及只读 SQLite 任务库适配器（`mode=ro`，不会创建或迁移数据库）。

## 限制

- 这是本地库和命令行，不是服务，没有接模型调用。`usage` 里的 `tokens` 与 `cost` 是 `UNKNOWN`；预算按序列化 UTF-8 字节计，不拿字符数冒充 token。
- 哈希只证明字节一致，不证明作者身份、内容真实或来源独立。安装配置由宿主管理，**同一系统用户并不构成对抗性隔离边界**。
- 演示里的"知识时点"是人为设定的保守界，不是真实发布时间。
- 没有评估过"装载弹匣后模型回答更好"；测试只验证装载规则本身。

## 开发说明

架构设计和提示词设计由作者完成，代码实现借助了 AI 编程工具，并通过上面的测试验证。

## 许可

MIT，见 [LICENSE](LICENSE)。
