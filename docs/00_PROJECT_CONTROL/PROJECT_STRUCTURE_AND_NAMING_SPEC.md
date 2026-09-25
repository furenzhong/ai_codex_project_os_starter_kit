# 结构与命名

## 源工具包

根目录保留项目入口、配置与公开使用文件：`README.md`、`README.en.md`、`AGENTS.md`、`CLAUDE.md`、`PROJECT_BOOTSTRAP_INPUT.md`、`project-os.json`、`LICENSE`、`CONTRIBUTING.md`。

- `docs/00_PROJECT_CONTROL/`：本仓库治理、状态和文档索引。
- `docs/01_PRODUCT/`：工具包的目标与接入流程。
- `docs/02_TECH/`：实现、映射及执行合同。
- `docs/03_DELIVERY/`：接入、验收和使用试验。
- `docs/04_ISSUES/`：问题与决策。
- `docs/05_HANDOFF/`：交接、历史会话与本仓库验证记录。
- `docs/06_ARCHIVE/`：需要保留的被替代材料，按需建立。
- `scripts/project_os.py`：跨平台 Python 标准库工具。
- `tests/`：隔离临时仓库中的行为回归。
- `.agents/skills/`：可选的源仓库工作流技能，不随接入自动安装到全局。
- `examples/`：虚构的映射与合同示例，不是有效任务或生产事实。

现有 `*_v1.md` 文件名保持稳定，本次兼容修订用内容说明。模板放在相应层的 `templates/`，不在每次接入时整套复制。

## 接入后的目标项目

尊重原项目布局。默认只增加 `project-os.json`、四份最小治理文档与本地检查工具，并在现有 Agent 入口追加引用。默认文档是：

```text
project-os/
  RULES.md
  STATUS.md
  HANDOFF.md
  DECISIONS.md
```

`tasks/` 和 `evidence/` 在实际委派与验证时按需使用。已有等价文档通过 manifest 映射，不要求另建一套目录。业务代码、产品文档、Git remote 和分支命名保持项目自身约定。

工作材料、当前权威、证据和归档材料的生命周期见 [文档生命周期](DOCUMENT_LIFECYCLE.md)。`docs/06_ARCHIVE/` 默认不进入 AI 上下文；归档不是自动删除的许可。

## 文件和任务命名

名称表达用途，不用 final/new/copy 区分版本。任务与证据用可追溯 ID 或日期命名。Python、Web 等技术命名遵循目标项目自身规则；本工具包不要求前后端、规则引擎或特定语言。

## 变更职责

新正式文档登记到 [目录](DOCUMENT_CATALOG.md)。结构变更记录到 [决策](../04_ISSUES/DECISION_LOG.md)。日常状态只在 [当前状态](PROJECT_CURRENT_STATUS.md) 更新。
