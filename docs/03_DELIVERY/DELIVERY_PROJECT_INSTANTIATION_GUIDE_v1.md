# 把治理接入当前项目

适用请求：“把这个仓库链接部署到我现在开发的项目中”。默认做已有项目的增量接入。源工具包仅提供方法和工具，目标项目继续保留自己的身份。

## 1. 确定源与目标

先确认用户当前工作区的项目根目录、Git remote、现有改动和 Agent 规则。在单独目录下载源工具包。不要因 shell 切到了源目录，就将源目录当成目标。也不要把 target 的 origin 改为工具包的 origin。

用户已经明确要求接入时，读现状、做计划、增量修改与检查属于本次工作；无需逐项再次批准。只有无法确定目标、相互冲突的业务要求或超出授权的外部动作才向用户提出具体问题。

工具要求 Python 3.10+ 和 Git。它不下载依赖、不调用模型、也不运行项目中的业务命令。

## 2. 先复用，再补缺口

阅读目标项目当前规则和最小状态链，识别以下职责是否已经存在：稳定规则、当前事实、未完成现场、重要决定。已经存在就映射；没有才使用默认文件。

从目标事实提取已确认要求、待验证假设与观察结果，不填入源工具包自身的阶段。PRD、架构、接口和风险模板按实际缺口选择；不要求目标先建立前后端或 Mock 应用。

只读预览与执行（从目标根目录运行）：

```text
python ../awoo-governance-kit/scripts/project_os.py plan --target .
python ../awoo-governance-kit/scripts/project_os.py apply --target .
```

plan 有冲突时先处理具体原因。apply 保留已有文件原文，只创建缺失文件并追加一次受管入口；重复执行不会刷新用户状态。不要用删除旧文件、重建 Git 或覆盖整个目录来消除冲突。

## 3. 已有治理的映射

提供 JSON 文件，字段可以局部指定；未指定部分用默认值。例如目标已有如下文档：

```json
{
  "sources": {
    "rules": "AGENTS.md",
    "status": "docs/CURRENT.md",
    "handoff": "docs/HANDOFF.md",
    "decisions": "docs/DECISIONS.md"
  },
  "tasks_dir": "docs/tasks",
  "evidence_dir": "docs/evidence"
}
```

将该映射存为目标中的 `work/adoption.json` 后，用相同映射运行 plan 和 apply：

```text
python ../awoo-governance-kit/scripts/project_os.py plan --target . --mapping work/adoption.json
python ../awoo-governance-kit/scripts/project_os.py apply --target . --mapping work/adoption.json
```

映射文件参数相对执行命令的当前目录，文件中的路径字段相对目标根目录。路径不能越界、指向 .git 或借符号链接写到外面。示例文件是路径形状示例，必须先根据目标核对。若已有相同职责却使用不同术语，由 AI 在现有文档中最小补充职责说明，不建立第二份事实。

## 4. 接入后 AI 要做什么

1. 检查源未被业务化，目标原有代码、文件与 remote 未被替换。
2. 从实际材料补全最小目标、要求、假设和事实来源；没证据的状态标为未知。
   对开发过程材料按 [文档生命周期](../00_PROJECT_CONTROL/DOCUMENT_LIFECYCLE.md) 运行一次只读 `inventory`，识别与当前任务有关的候选、旧方案及证据；未归类不等于可删除。新建 RULES 已含最小收敛规则；若映射已有 rules，AI 应在该唯一来源补充同等读取和收尾纪律，不复制整套指南。已有文档原位采用，不在首次接入时自动搬动或清空历史。
3. 运行 `python scripts/project_os.py check --target .`，解释错误、提醒与未验证范围。
4. 按 [治理试验](GOVERNANCE_TRIAL.md) 做一次独立接手。不能把同一上下文复述答案当成新会话验证。
5. 用简短回执告诉用户能否接续、发现了什么、还没测什么、是否需要其决策。用户不必给模板逐项打分。

## 5. 更新、冲突与卸载

apply 只完成接入，不自动升级已经安装的脚本或 manifest。源工具包更新时，先比较来源 revision 和本次变化。项目自行填写的状态、决定和业务要求不由模板覆盖。受管入口或工具代码已被修改时，先看差异并合并，再重新检查；当前工具不提供强制覆盖升级开关。

v1.2 的生命周期更新包括新版脚本和 rules 中的最小收敛规则。旧版项目不会因重新运行 apply 自动得到新规则；对照 diff 合并脚本与原有规则后，记录实际采用版本及来源，保留项目自有内容，再做相关检查和文档收敛演练。不要只修改版本号宣称完成升级。

如需撤销接入，利用接入 diff 删除本次新增且未被继续使用的文件、移除标记包围的入口块。不要删除已积累项目事实的治理目录。工具不自动卸载；Git 提交可以为变更提供审查和恢复依据，但接入过程不会替用户 commit 或 push。

## 6. 权限与工具适配

AGENTS 是共享规则来源。CLAUDE 兼容入口使用 import，并核对实际启动方式是否加载；某些运行模式会跳过项目规则。Markdown 描述应做什么，不等于操作系统限制。执行权限由现有宿主配置和用户授权决定，不在接入时自动扩大。

协作任务按 [Harness 合同](../02_TECH/HARNESS_CONTRACT.md) 记录版本、写入归属和验收证据。源工具包不会把业务任务派给外部模型。
