# DOCUMENT_CATALOG.md 模板

- 文档类型：基线文档 / 控制文档
- 当前状态：active
- 当前版本：v1.0
- 最后更新时间：[YYYY-MM-DD]
- 当前负责人：[项目负责人姓名 / AI / Codex]
- 是否为当前有效版本：是

---

# [项目名称] 文档目录账本

## 1. 文档作用

这份文档用于作为整个项目文档系统的**正式目录账本**，统一记录：
- 当前有哪些正式文档
- 每份文档属于什么类型
- 每份文档当前是否有效
- 每份文档的用途是什么
- 每份文档由谁维护
- 新接手者应该优先看哪些文档
- 哪些文档已经过时或归档

它的目标不是简单列文件名，而是建立一个**可治理、可检索、可追踪、可恢复**的文档索引系统。

---

## 2. 为什么必须有文档目录账本

当项目开始使用：
- 多轮 AI 会话
- 多轮 Codex 开发
- 大量模板文档
- 频繁交接
- 多个阶段迭代

文档会快速增长。

如果没有目录账本，常见问题会马上出现：
- 文档越来越多，但不知道哪些是正式文档
- 不知道哪份才是当前有效版本
- 同名或同主题文档互相冲突
- 新增文档没有纳入治理系统
- 新 AI 无法快速知道先看什么
- 旧文档误导当前执行

所以，这份文档的作用是：

**把“所有项目文档”从散落文件，变成一个有状态的文档系统。**

---

## 3. 使用原则

### 原则 1：没有进入目录账本的文档，不算正式项目文档
临时草稿可以存在，但如果一份文档要进入正式项目治理系统，就必须进入本目录账本。

### 原则 2：目录账本记录的是“文档状态”，不是只记录文件名
每份文档都至少应有：
- 文档名
- 文档类型
- 当前状态
- 当前版本
- 是否有效
- 用途说明
- 所在目录
- 负责人

### 原则 3：同主题文档必须明确谁是当前有效版本
不能让多个版本并列存在而不说明哪份有效。

### 原则 4：归档文档不能混在当前有效文档里
旧文档必须保留，但必须明确标记状态。

### 原则 5：目录账本应成为新 AI / 新协作者的检索入口之一
新接手者不用扫文件树，而是先看目录账本。

---

## 4. 文档分类体系

建议将文档至少分为以下类别：

### 4.1 Project Control
项目控制类文档
示例：
- `PROJECT_MASTER_INDEX.md`
- `PROJECT_CURRENT_STATUS.md`
- `PROJECT_STRUCTURE_AND_NAMING_SPEC.md`
- `DOCUMENT_CATALOG.md`
- `DOCUMENT_GOVERNANCE_SYSTEM.md`

### 4.2 Product
产品类文档
示例：
- `PRODUCT_PRD_v1.md`
- `PRODUCT_MVP_SCOPE.md`
- `PRODUCT_USER_FLOW.md`

### 4.3 Tech
技术类文档
示例：
- `TECH_API_JSON_SPEC_v1.md`
- `TECH_RULES_ENGINE_SPEC_v1.md`
- `TECH_ARCHITECTURE.md`

### 4.4 Delivery
开发交付类文档
示例：
- `DELIVERY_CODEX_TASK_BREAKDOWN_v1.md`
- `IMPLEMENTATION_PROGRESS.md`
- `TEST_CASES_AND_ACCEPTANCE.md`

### 4.5 Issues
问题与治理类文档
示例：
- `ISSUE_BUG_REGISTER.md`
- `ISSUE_TECH_QUESTION_REGISTER.md`
- `DECISION_LOG.md`
- `RISK_REGISTER.md`

### 4.6 Handoff
交接类文档
示例：
- `HANDOFF_CURRENT.md`
- `AI_CONTEXT_BRIEF.md`
- `NEXT_SESSION_STARTER.md`
- `SESSION_SUMMARIES/*`

### 4.7 Archive
归档类文档
示例：
- 旧版本 PRD
- 已废弃架构方案
- 已替代的历史文档

---

## 5. 文档状态规范

每份文档至少应有以下状态之一：

- `draft`：草稿
- `active`：当前有效
- `superseded`：已被新版本替代
- `paused`：暂时停用
- `archived`：已归档

### 状态使用建议
- 基线文档通常应为 `active`
- 被替代的旧基线应为 `superseded`
- 不再参与当前执行的旧文档应为 `archived`
- 尚未定稿的探索文档应为 `draft`

---

## 6. 文档目录总表模板

这是目录账本的核心部分。

| 文档名 | 分类 | 文档类型 | 当前状态 | 当前版本 | 是否当前有效 | 所在目录 | 用途 | 负责人 | 上游文档 | 下游文档 | 最后更新时间 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `PROJECT_MASTER_INDEX.md` | Project Control | 基线文档 | active | v1.0 | 是 | `/docs/00_PROJECT_CONTROL/` | 项目总入口 | [负责人] | 无 | `PROJECT_CURRENT_STATUS.md` | [YYYY-MM-DD] |
| `PROJECT_CURRENT_STATUS.md` | Project Control | 基线文档 | active | v1.0 | 是 | `/docs/00_PROJECT_CONTROL/` | 当前真实状态 | [负责人] | `PROJECT_MASTER_INDEX.md` | `HANDOFF_CURRENT.md` | [YYYY-MM-DD] |
| `PROJECT_STRUCTURE_AND_NAMING_SPEC.md` | Project Control | 基线文档 | active | v1.0 | 是 | `/docs/00_PROJECT_CONTROL/` | 结构与命名规范 | [负责人] | `PROJECT_MASTER_INDEX.md` | 全部文档 | [YYYY-MM-DD] |
| `DOCUMENT_CATALOG.md` | Project Control | 控制文档 | active | v1.0 | 是 | `/docs/00_PROJECT_CONTROL/` | 文档目录账本 | [负责人] | `PROJECT_MASTER_INDEX.md` | 全部文档 | [YYYY-MM-DD] |
| `[PRODUCT_PRD_v1.md]` | Product | 基线文档 | active | v1.0 | 是 | `/docs/01_PRODUCT/` | 产品定义 | [负责人] | `PROJECT_MASTER_INDEX.md` | `DELIVERY_CODEX_TASK_BREAKDOWN_v1.md` | [YYYY-MM-DD] |
| `[TECH_API_JSON_SPEC_v1.md]` | Tech | 基线文档 | active | v1.0 | 是 | `/docs/02_TECH/` | API 与 JSON 规范 | [负责人] | `PRODUCT_PRD_v1.md` | 后端实现文档 | [YYYY-MM-DD] |

### 字段说明
| 字段 | 说明 |
|---|---|
| 文档名 | 文件名称 |
| 分类 | Project Control / Product / Tech / Delivery / Issues / Handoff / Archive |
| 文档类型 | 基线文档 / 执行文档 / 记录文档 / 交接文档 / 归档文档 |
| 当前状态 | draft / active / superseded / paused / archived |
| 当前版本 | 如 v1.0 / v1.1 / v2 |
| 是否当前有效 | 是 / 否 |
| 所在目录 | 文件所在路径 |
| 用途 | 一句话说明文档干什么 |
| 负责人 | 当前主要维护者 |
| 上游文档 | 本文档通常依赖什么 |
| 下游文档 | 本文档会影响什么 |
| 最后更新时间 | 最近更新时间 |

---

## 7. 当前必读文档清单

这一节用于告诉新 AI / 新协作者：先看哪些文档。

### 7.1 全局必读
- `PROJECT_MASTER_INDEX.md`
- `PROJECT_CURRENT_STATUS.md`
- `PROJECT_STRUCTURE_AND_NAMING_SPEC.md`
- `DOCUMENT_GOVERNANCE_SYSTEM.md`
- `HANDOFF_CURRENT.md`

### 7.2 当前阶段必读
- [当前阶段相关文档 1]
- [当前阶段相关文档 2]
- [当前阶段相关文档 3]

### 7.3 当前模块必读
- [当前模块文档 1]
- [当前模块文档 2]

### 7.4 当前不建议优先阅读的文档
- [旧版文档 1]
- [已归档文档 1]
- [已失效方案文档 1]

---

## 8. 当前有效基线文档清单

这一节只列“当前有效”的核心基线文档。

| 文档名 | 分类 | 作用 | 为什么必须看 |
|---|---|---|---|
| `PROJECT_MASTER_INDEX.md` | Project Control | 总入口 | 决定阅读顺序 |
| `PROJECT_CURRENT_STATUS.md` | Project Control | 当前状态 | 决定现在做到哪 |
| `PROJECT_STRUCTURE_AND_NAMING_SPEC.md` | Project Control | 结构规范 | 决定文件怎么放、怎么命名 |
| `[PRODUCT_PRD_v1.md]` | Product | 产品定义 | 决定做什么 |
| `[TECH_API_JSON_SPEC_v1.md]` | Tech | 接口规范 | 决定怎么对接 |
| `[TECH_RULES_ENGINE_SPEC_v1.md]` | Tech | 规则逻辑 | 决定怎么判断 |
| `[DELIVERY_CODEX_TASK_BREAKDOWN_v1.md]` | Delivery | 开发任务 | 决定怎么推进 |

### 原则
如果其他文档与这里列出的当前有效基线冲突，以这里列出的为准。

---

## 9. 已归档 / 已替代文档清单

这一节用于防止旧文档误导当前执行。

| 文档名 | 当前状态 | 被谁替代 / 归档原因 | 是否仍可参考 |
|---|---|---|---|
| `[旧文档名 1]` | superseded | 被 `[新文档名]` 替代 | 是 |
| `[旧文档名 2]` | archived | 已无当前执行价值 | 否 |

### 使用原则
- `superseded` 文档可用于理解历史，但不能作为当前执行依据
- `archived` 文档默认不进入当前执行链路

---

## 10. 新文档纳入规则

当项目产生新文档时，建议按以下流程纳入：

1. 判断它是否值得成为正式项目文档
2. 确定分类与文档类型
3. 指定状态、版本、负责人
4. 写入目录总表
5. 若是基线文档，写入“当前有效基线文档清单”
6. 若替代旧文档，更新旧文档状态

### 值得纳入正式目录的典型情况
- 会被多次引用
- 会影响多个模块
- 会参与交接
- 会成为未来执行依据
- 需要长期追踪

### 不建议立即纳入的情况
- 临时头脑风暴草稿
- 一次性说明
- 未成型的碎片化记录

---

## 11. 文档变更治理规则

### 当文档状态变化时
应同步更新目录账本中的以下字段：
- 当前状态
- 当前版本
- 是否当前有效
- 最后更新时间
- 替代关系（如有）

### 当新版本替代旧版本时
- 新文档加入目录
- 旧文档状态改为 `superseded`
- 旧文档“是否当前有效”改为“否”
- 在归档/替代清单中记录

### 当文档归档时
- 状态改为 `archived`
- 从当前有效基线清单中移除
- 加入归档清单

---

## 12. 目录维护节奏建议

### 每次新增正式文档后
- 立即补录到目录账本

### 每次阶段切换后
- 回顾当前有效基线文档清单
- 检查是否有文档需要升版或归档

### 每次重要交接前
- 检查目录是否完整
- 检查 handoff 中引用的文档是否都已登记

### 每周或每轮大推进后
- 清理过时文档
- 标记被替代文档
- 检查是否存在未入目录的正式文档

---

## 13. 推荐视图：按用途筛选

为了提高可读性，建议在总表之外增加若干“按用途筛选视图”。

### 13.1 只看当前有效文档
列出所有：
- 状态为 `active`
- 是否当前有效 = 是

### 13.2 只看交接相关文档
列出：
- `HANDOFF_CURRENT.md`
- `AI_CONTEXT_BRIEF.md`
- `NEXT_SESSION_STARTER.md`
- `SESSION_SUMMARIES/*`

### 13.3 只看问题治理文档
列出：
- `ISSUE_BUG_REGISTER.md`
- `ISSUE_TECH_QUESTION_REGISTER.md`
- `DECISION_LOG.md`
- `RISK_REGISTER.md`

### 13.4 只看可直接给 Codex 的文档
列出：
- PRD
- API/JSON Spec
- Rules Engine Spec
- Codex Task Breakdown
- 当前状态文档
- 当前 handoff 文档

---

## 14. 当前目录健康检查

用于判断文档治理系统是否开始失控。

| 检查项 | 当前状态 | 备注 |
|---|---|---|
| 是否存在项目总索引 | [是/否] | [备注] |
| 是否存在当前状态文档 | [是/否] | [备注] |
| 是否存在当前交接文档 | [是/否] | [备注] |
| 是否存在问题治理文档 | [是/否] | [备注] |
| 是否存在决策日志 | [是/否] | [备注] |
| 新增正式文档是否均已入账 | [是/否] | [备注] |
| 是否存在已失效但未标记的文档 | [是/否] | [备注] |
| 是否存在同主题多版本冲突 | [是/否] | [备注] |

### 健康判断建议
- 若有 2 项以上为“否”，建议优先做文档整理，而不是继续扩写新文档。

---

## 15. AI / Codex 使用规则

### 给 AI 的建议
- 新接手项目时，先看目录账本，再决定读哪些文档
- 不要默认文件夹里所有文档都当前有效
- 新建正式文档后，记得补入目录账本

### 给 Codex 的建议
- Codex 任务上下文中应明确给出“当前有效文档清单”
- 不要把已归档或被替代文档作为当前实现依据
- 若发现文档引用冲突，应先指出冲突再继续

### 给 Codex 的目录约束提示模板
```text
你正在接手一个已有文档治理系统的项目。
请仅以以下当前有效文档为准：
- [文档 1]
- [文档 2]
- [文档 3]

不要参考：
- [已归档文档 1]
- [已被替代文档 1]

如果你发现当前目录账本与实际文件状态冲突，请先指出冲突，不要擅自按旧文档实现。
```

---

## 16. AI 阅读提示

- 这份文档是否当前有效：是
- 这份文档适合什么时候看：需要知道项目有哪些正式文档、先看哪些、哪些已过时时
- 阅读优先级：最高
- 上游文档：`PROJECT_MASTER_INDEX.md`
- 下游文档：全部正式文档
- 阅读建议：先看第 6、7、8、9、14 节

---

## 17. 变更记录

- [YYYY-MM-DD]：创建 v1.0 模板
- [YYYY-MM-DD]：补充当前有效基线清单
- [YYYY-MM-DD]：补充归档/替代文档清单
- [YYYY-MM-DD]：补充目录健康检查
- [YYYY-MM-DD]：补充结构与命名基线条目

---

## 18. 快速复制版（最小可用）

如果你想先快速建立一个可用版 `DOCUMENT_CATALOG.md`，至少保留以下内容：

1. 文档目录总表
2. 当前必读文档清单
3. 当前有效基线文档清单
4. 已归档 / 已替代文档清单
5. 新文档纳入规则
6. 目录健康检查

只要这 6 部分存在，这份文档就已经具备基本的文档账本能力。
