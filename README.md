# Awoo Vibe Coding Governance

[English](README.en.md) · 简体中文

让 AI 换会话、换模型、换执行工具之后，仍能接着把同一个项目做对。

Awoo Vibe Coding Governance 是一个可接入**已有项目**的轻量治理工具包。它帮助 AI 找到有效要求、当前事实、未完成现场和验收依据，并提供增量接入与检查脚本。你可以直接把这个仓库链接发给正在开发项目的 AI。

适合长期用 Codex、Claude Code 等工具迭代项目的人。一次性小任务可以只借用其中的原则，不必建立整套文档。它不会自动开发你的业务，也不要求特定模型、技术栈或多 Agent。

## 最简单的用法

在你正在开发的项目中，把下面这段话发给 AI：

```text
请把 https://github.com/furenzhong/awoo-vibe-coding-governance 的文档治理
接入我当前正在开发的项目。

先按该仓库的接入指南识别源工具包与目标项目，复用我已有的规则和事实来源，
增量补齐缺口。保留项目代码、已有文档、未提交改动、Git 历史和 remote。
不要把工具包自己的产品定位或状态复制成我的项目事实。

完成后运行机器检查和一次独立接手演练。告诉我检查发现什么、实际验证了什么、
还有什么未验证，以及是否有必须由我判断的问题。不需要我逐项填治理表格。
```

AI 的详细操作入口是 [接入指南](docs/03_DELIVERY/DELIVERY_PROJECT_INSTANTIATION_GUIDE_v1.md)。原项目资料已经足够时，不应要求你重复填写输入表或确认普通实现选择。

## 它解决什么

| 常见问题 | 对应机制 |
|---|---|
| 新会话重新讨论已经定好的事 | 当前事实与决定有明确来源，入口按需读取 |
| 多份“当前状态”互相矛盾 | 同一事实只维护一处，交接和简报引用它 |
| AI 说做完，但不知道验证了什么 | 交付绑定版本、检查结果和证据，验收单独表达 |
| Codex 交给 Claude Code 后难以接回 | 明确任务基线、写入归属、会话、交付及恢复合同 |
| 把源仓库部署成了另一套业务项目 | 接入前核对源 / 目标身份，保留目标 Git 与业务内容 |
| 文档越写越多，不知道有没有用 | AI 进行接手和故障演练，报告结果与维护负担 |

先验证最关键的不确定性。页面流程可以用 Mock；模型效果、真实接口或生成质量需要相应的实际证据。模板不会要求每个项目先建前后端和规则引擎。

## 接入会增加什么

默认新增四份小文档；已有等价文档时可以直接映射，避免再维护一套。

```text
你的项目/
  project-os.json             # 权威文件位置与工具包来源
  AGENTS.md                   # 保留原文，追加治理索引
  CLAUDE.md                   # 保留原文，追加共享规则 import
  scripts/project_os.py       # 本地检查工具
  project-os/
    RULES.md                  # 稳定规则
    STATUS.md                 # 当前事实、假设、目标
    HANDOFF.md                # 未完成现场与恢复线索
    DECISIONS.md              # 重要选择及依据
```

任务与证据目录按实际工作需要使用。PRD、API、风险登记等较重模板留在工具包里按需取用，**不整套复制到每个项目**。初始文档需要 AI 从你的项目事实中补齐，文件存在不代表接入已经验收。

为兼容已有接入，`project-os.json`、`project-os/` 与 `scripts/project_os.py` 保留原名；不需要为了品牌更名迁移项目文件。

## 手动执行 / 检查命令

需要 Python 3.10+ 和 Git；不需要模型 API key 或第三方 Python 包。Windows PowerShell、macOS、Linux 可用同一 Python 入口。以下命令在**目标项目根目录**执行，源工具包放在旁边：

```text
git clone https://github.com/furenzhong/awoo-vibe-coding-governance.git ../awoo-governance-kit
python ../awoo-governance-kit/scripts/project_os.py plan --target .
python ../awoo-governance-kit/scripts/project_os.py apply --target .
python scripts/project_os.py check --target .
python scripts/project_os.py snapshot --target . --json
```

- `plan` 只读列出接入操作和冲突，AI 核对后可在既有授权内执行 `apply`。
- `apply` 增量创建 / 追加；重复执行不覆盖用户内容。工具遇到冲突会报告，不会用覆盖整个项目来解决。
- `check` 检查声明的路径、入口、任务与证据一致性；不调用模型、业务服务或网络。
- `snapshot` 输出当前可观察信息，不自动改写项目状态。

已有文档通过 `--mapping` 接入，见 [映射示例](examples/adoption-mapping.json) 和 [接入指南](docs/03_DELIVERY/DELIVERY_PROJECT_INSTANTIATION_GUIDE_v1.md)。示例路径必须替换成目标的真实路径。首次采用和已有部署升级是不同工作；更新时先比较差异，保留项目自有内容。

## AI 在使用，我怎么知道它有用

让 AI 交付一张很短的回执，而不是让你逐项审查模板：

```text
机器检查：通过 / 有问题；附实际报告
独立接手：通过 / 失败 / 未测；能否找对目标、现场和下一步
异常演练：识别了什么，仍漏掉什么
实际使用：重复工作、用户纠偏、文档维护负担是否有记录
需要你决定：没有，或一个具体问题
```

首次接入和读取 / 协作机制大改时，按 [治理试验](docs/03_DELIVERY/GOVERNANCE_TRIAL.md) 在隔离副本中演练：新会话接手、过期陈述、缺验收证据、中断恢复。日常只检查相关变化，不每轮重复整套演练，也不自动创建监控或付费调用。

**机器检查通过只证明被检查的结构与声明满足规则。** 它不能证明产品质量、文档每句话的真实性，或 Agent 实际遵守了要求。没有做过的演练明确写“未测”；有问题就给出证据和最小修正。当前版本的实测范围和对应证据见 [当前状态](docs/00_PROJECT_CONTROL/PROJECT_CURRENT_STATUS.md)。

## Codex → Claude Code 等协作

[Harness 合同](docs/02_TECH/HARNESS_CONTRACT.md) 提供工具中性的派工与接回约定：目标和基线 → 独立执行 → 可核查交付 → 验收 → 更新唯一状态。

它目前是合同、示例和本地回执检查，**不是已经实现的跨模型调度器**。执行者、模型和 CLI 由项目选择；工作目录隔离不等于数据库、端口和外部账户隔离。中断后先查已有任务与会话，再决定续跑，避免重复执行已经发生的操作。

## 阅读与参与

- [治理原则](docs/00_PROJECT_CONTROL/DOCUMENT_GOVERNANCE_SYSTEM.md)：事实、要求、假设和验收的归属。
- [当前实现与局限](docs/00_PROJECT_CONTROL/PROJECT_CURRENT_STATUS.md)：以实际记录为准。
- [贡献指南](CONTRIBUTING.md)：用具体失败和验证结果改进工具包。
- [MIT License](LICENSE)：允许复制、修改、商业使用与再分发，保留许可证声明。

共享规则维护在 `AGENTS.md`，`CLAUDE.md` 用作兼容入口。可选 `.agents/skills/` 仅为相应工作流提供指导，接入工具不会自动修改你的全局技能或模型配置。
