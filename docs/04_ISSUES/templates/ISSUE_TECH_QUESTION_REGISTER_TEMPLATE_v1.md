# ISSUE_TECH_QUESTION_REGISTER.md 模板

- 文档类型：记录文档
- 当前状态：active
- 当前版本：v1.0
- 最后更新时间：[YYYY-MM-DD]
- 当前负责人：[项目负责人姓名 / AI / Codex]
- 是否为当前有效版本：是

---

# [项目名称] 技术问题登记簿

## 1. 文档作用

这份文档用于统一记录项目中的 **技术问题（Tech Questions）**，确保所有尚未完全定论、需要分析、需要决策、需要跟踪的技术议题，都有明确记录和状态。

它要解决的核心问题是：
- 技术讨论散落在不同聊天里
- 同一个问题被反复问
- 已经分析过的问题没有沉淀
- 已经有临时结论，但没人知道是否定稿
- Bug、需求变更、架构问题、技术债混在一起

---

## 2. 什么是 Tech Question

Tech Question 指的是：

**项目推进过程中出现的、尚未完全定论的技术性问题、架构性问题、边界定义问题、实现策略问题、配置策略问题、工程治理问题。**

它不一定已经表现为错误，但它会影响后续的实现方式、扩展方式、维护方式或决策质量。

---

## 3. 使用原则

### 原则 1：一个问题可以暂时没有答案，但不能没有状态
至少应标记为：
- `open`
- `analyzing`
- `decision_needed`
- `resolved`
- `deferred`
- `obsolete`

### 原则 2：不要把“想到一个疑问”直接当结论
问题、分析、结论、决策要分层记录。

### 原则 3：优先记录“会影响后续实现”的问题
优先记录：
- 会影响多个模块
- 会影响接口或数据结构
- 会影响规则引擎
- 会影响 Codex 实现路径
- 会导致未来反复讨论

### 原则 4：如果问题已经拍板，应同步写入 Decision Log
Tech Question 不是最终结论仓库。

---

## 4. 技术问题状态流转规范

### 状态枚举
- `open`
- `analyzing`
- `decision_needed`
- `resolved`
- `deferred`
- `obsolete`
- `reopened`

### 推荐流转路径
```text
open -> analyzing -> decision_needed -> resolved
```

---

## 5. 技术问题分类建议

- `Architecture`
- `Data Model`
- `Rule Strategy`
- `Config Strategy`
- `Performance`
- `Integration`
- `Governance`
- `Classification`

---

## 6. 技术问题 ID 规范

建议统一使用：

```text
TQ-001
TQ-002
TQ-003
```

---

## 7. 技术问题总表模板

| Question ID | 标题 | 类型 | 当前状态 | 提出日期 | 当前负责人 | 影响范围 | 当前结论 | 下一步 |
|---|---|---|---|---|---|---|---|---|
| [TQ-001] | [问题标题] | [Architecture / Data Model / Rule Strategy] | [open / analyzing / decision_needed / resolved] | [YYYY-MM-DD] | [负责人] | [影响范围] | [简述] | [简述] |

---

## 8. 单条 Tech Question 详细模板

## [TQ-001] [技术问题标题]

### 8.1 基本信息
- Question ID：[TQ-001]
- 标题：[技术问题标题]
- 类型：[Architecture / Data Model / Rule Strategy / Config Strategy / Performance / Integration / Governance / Classification]
- 当前状态：[open / analyzing / decision_needed / resolved / deferred / obsolete / reopened]
- 当前负责人：[姓名 / AI / Codex]
- 提出日期：[YYYY-MM-DD]
- 最后更新时间：[YYYY-MM-DD]

### 8.2 问题描述
[写清楚问题到底是什么]

### 8.3 问题背景
[说明为什么会出现这个问题，当前上下文是什么]

### 8.4 当前影响范围
- 影响模块：[API / Frontend / Backend / Rules Engine / Overlay / Docs / Delivery]
- 是否影响当前阶段：[是/否]
- 是否影响多个模块：[是/否]
- 是否影响基线文档：[是/否]

### 8.5 当前已知选项

#### 选项 A：[名称]
- 做法：[说明]
- 优点：[说明]
- 风险/缺点：[说明]

#### 选项 B：[名称]
- 做法：[说明]
- 优点：[说明]
- 风险/缺点：[说明]

### 8.6 当前分析
[写当前已经做过的思考、比较、验证、结论趋势]

### 8.7 当前临时结论
[如果已有倾向，写在这里；如果没有可写“待分析”]

### 8.8 当前是否需要拍板
- [是/否]
- 若是，拍板人：[项目负责人 / 产品 / 技术负责人 / AI 辅助后由人拍板]

### 8.9 下一步动作
- [动作 1]
- [动作 2]
- [动作 3]

### 8.10 关联决策
- [Decision ID 或“暂无”]

### 8.11 关联文档
- [文档名 1]
- [文档名 2]
- [文档名 3]

### 8.12 处理记录
- [YYYY-MM-DD]：提出问题
- [YYYY-MM-DD]：完成初步方案对比
- [YYYY-MM-DD]：形成临时结论
- [YYYY-MM-DD]：正式拍板并同步 Decision Log

### 8.13 最终结论（问题 resolved 后填写）
[填写明确结论]

---

## 9. 推荐处理流程

### 当发现一个技术问题时
1. 先判断它是否真的是技术问题，而不是 bug 或需求变更
2. 若值得长期追踪，则加入总表
3. 若影响较大，则补详细条目
4. 标记当前状态为 `open`

### 当开始分析时
1. 更新状态为 `analyzing`
2. 补充背景、影响范围、选项对比
3. 记录当前临时结论

### 当问题解决后
1. 更新状态为 `resolved`
2. 写清最终结论
3. 如属重要结论，写入 `DECISION_LOG.md`
4. 如影响基线文档，更新对应基线文档

---

## 10. 给 Codex 的技术问题探索提示模板

```text
当前项目存在一个技术问题，请你不要直接大改系统，而是基于现有基线文档，从工程角度协助分析。

【问题 ID】
[TQ-001]

【问题标题】
[标题]

【问题背景】
[背景]

【当前候选方案】
- 方案 A：...
- 方案 B：...

【你要做的事】
1. 从工程实现角度比较两种方案
2. 说明对当前项目结构的影响
3. 说明对后续扩展的影响
4. 给出你建议的倾向方案，但不要擅自改动无关代码
```
