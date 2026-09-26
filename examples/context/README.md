# Context example / 上下文示例

This fictional task illustrates **an old result arriving while a correction is still pending**. It is deliberately not accepted. No CLI ran, no test passed, and the commit/session/time values are placeholders. Replace them with observations. Do not copy this directory wholesale into a live task directory.

虚构场景：执行者拿到 ctx-001；负责人发现漏交用户的“只允许主动清理”约束，形成 ctx-002，但尚未送达原会话。原执行者交回旧版本结果，需要先审查其中自动归档的行为，保留可复用的状态导出部分。不能直接改版本号或填写假的采用证据来通过检查。

| 本例文件 | 在目标项目中的对应路径 |
|---|---|
| [task.json](task.json) | `project-os/tasks/handoff-export.json` |
| [context-001.md](context-001.md)、[context-002.md](context-002.md) | `project-os/tasks/handoff-export/context-001.md`、`context-002.md` |
| [coordinator.json](coordinator.json)、[executor.json](executor.json) | 同任务子目录内的各身份检查点 |
| [correction-001.json](correction-001.json) | 同任务子目录内的纠偏 |
| [receipt.json](receipt.json) | 同任务子目录内的原始回执 |
| [check-example.txt](check-example.txt) | 同任务子目录内的格式占位；回执中 exit 1 展示检查未成功，不是实测失败 |
| [source-decision.md](source-decision.md) | `project-os/DECISIONS.md` 中的既有决定；不另造第二份当前决定 |

快照 hash 对应本目录实际内容，只有 CRLF 转 LF 后计算 SHA-256。移入项目时一旦改写内容或来源路径，须为实际派工生成实际快照和摘要。全零/全一 Git SHA 不存在，原样执行检查必然失败；这不是一个成功验收夹具。

后续可向原会话实际送达 ctx-002，保存输入和采用响应，再更新其检查点；或核实原写入者停止后转交给新身份。纠偏采用证据应保留其实际版本和影响分析，而不是仅引用会被覆盖的检查点。完整规则见 [任务上下文合同](../../docs/02_TECH/TASK_CONTEXT.md)。
