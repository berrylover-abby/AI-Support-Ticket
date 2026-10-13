# 开发记录 / Development Log

**更新日期 / Updated:** 2026-10-13

**当前进度 / Progress:** 已完成第 1–7 阶段及前端联调 / Build stages 1–7 and frontend integration checks completed

本项目是用于求职展示的轻量 Demo，重点体现 REST API、数据库持久化、结构化分析和人工审核。以下“天数”表示计划中的开发阶段，不代表实际连续日期。

This lightweight portfolio demo demonstrates REST APIs, database persistence, structured analysis, and human review. “Days” below refer to planned build stages rather than consecutive calendar dates.

## 第一天：建立项目基础 / Day 1: Project foundation

先创建 Python 虚拟环境并安装 Django 和 Django REST Framework，再建立项目配置 `config` 和工单模块 `tickets`。在设置中注册 DRF 和工单模块，通过迁移初始化 SQLite，启动开发服务器确认项目能运行。最后生成 `requirements.txt`、设置 `.gitignore` 并提交 Git，记录依赖并排除本地环境和数据库。

We created a Python virtual environment, installed Django and Django REST Framework, and generated the `config` project and `tickets` app. We registered both apps, initialized SQLite through migrations, and started the development server. We then recorded dependencies in `requirements.txt`, excluded local artifacts with `.gitignore`, and committed the project to Git.

## 第二天：建立工单数据与 API / Day 2: Ticket data and APIs

按 **Model → Migration → Serializer → View → URLs** 的顺序搭建功能：模型定义标题、描述和创建时间；迁移创建工单表；Serializer 验证输入并转换输出；View 处理请求；路由把网址连接到 View。随后注册 Django Admin、创建管理员账号，并验证工单保存以及创建、列表和详情接口。

We built the feature in this order: **Model → Migration → Serializer → View → URLs**. The model defines the title, description, and creation time; migrations create the table; the serializer validates input and converts output; views handle requests; and URL routes connect endpoints to views. We also registered the model in Django Admin, created an administrator account, and verified persistence and all three endpoints.

| 接口 / Endpoint | 用途 / Purpose |
| --- | --- |
| `POST /api/tickets/` | 创建并保存工单 / Create and persist a ticket |
| `GET /api/tickets/` | 获取列表，最新在前 / List tickets, newest first |
| `GET /api/tickets/{id}/` | 获取单张工单 / Retrieve one ticket |

## 第三天：定义人工审核流程 / Day 3: Human review workflow

为工单增加待分析、待审核、已确认和分析失败四种状态，并通过迁移更新数据库。`ai_result` 保存原始分析建议，四个 `reviewed_` 字段分别保存人工审核后的分类、优先级、摘要和回复。Admin 提供状态筛选和审核字段编辑，原始建议与状态设为只读。确认操作只允许待审核且审核内容完整的工单通过；已验证待分析工单不能直接确认。

We added four states: pending analysis, pending review, confirmed, and analysis failed. We migrated the database and separated original suggestions in `ai_result` from the four human-reviewed fields. Admin supports status filtering and review editing while keeping original suggestions and status read-only. The confirmation action requires a pending-review ticket with all review fields completed. We verified that pending-analysis tickets cannot be confirmed directly.

## 第四天：跑通模拟分析与错误恢复 / Day 4: Mock analysis and recovery

先在 `services.py` 编写模拟分析函数，返回 category、priority、summary 和 suggested reply。再用独立 Serializer 验证四个字段、分类与优先级的允许值，以及摘要和回复是否为空。保存函数只接受待分析或分析失败的工单，验证通过后保存建议、预填审核字段，并将状态更新为待审核。最后把分析函数连接到 Admin 操作菜单，并添加分析成功与验证失败的终端日志。

We first added a mock analysis function in `services.py` that returns category, priority, summary, and suggested reply. A dedicated serializer validates required fields, allowed categories and priorities, and non-empty text. The save function accepts only pending or failed tickets, stores validated suggestions, prefills review fields, and moves the ticket to pending review. We connected this workflow to an Admin action and added console logging for analysis success and validation failure.

已手动验证：分析成功后可以修改并确认，且原始建议保持不变；无效分类会使工单进入分析失败状态，原始工单仍保留；恢复合法输出后可以重试成功；成功日志能在终端显示。

Manual checks confirmed that reviewers can edit and confirm suggestions while preserving the original analysis; invalid categories produce an analysis-failed state without losing the ticket; corrected output allows a successful retry; and success logs appear in the terminal.

## 第五天：接入真实 LLM / Day 5: Real LLM integration

先准备 API key，并在终端环境变量中配置。由于本机 Windows 应用控制策略阻止了 SDK 依赖的原生 DLL，最终采用 Python 标准库直接调用 OpenAI Responses API，使用 `gpt-4.1-mini`。请求携带 JSON Schema 约束输出，再提取分析结果并交给已有 Serializer 验证。`TICKET_AI_MODE` 允许在 mock 和 openai 模式间切换。

We configured an API key through a terminal environment variable. Windows application control blocked a native dependency of the SDK, so the final implementation calls the OpenAI Responses API directly using Python's standard library and `gpt-4.1-mini`. A JSON Schema constrains model output, which is then extracted and validated by the existing serializer. `TICKET_AI_MODE` selects mock or openai mode.

随后将共享分析服务接到 API 创建流程：先保存工单，再同步分析；预期调用错误或输出验证失败时，保留工单并记录失败状态。Admin 支持对失败工单重试。调用层设置网络超时，并处理 HTTP、网络、无效 JSON、未完成输出和拒绝响应。

We connected the shared analysis service to API creation: persist the ticket first, then analyze synchronously. Expected request or validation failures preserve the ticket and record a failed state; Admin supports manual retries. The request layer sets a network timeout and handles HTTP errors, connection failures, invalid JSON, incomplete output, and refusals.

已手动验证真实分析与人工确认、API 自动分析，以及缺少 key 时返回 `201 Created` 和 `analysis_failed`、恢复 key 后对同一张工单重试成功。超时和拒绝响应已有处理代码，尚未单独模拟验证。重复扣费样例的优先级被模型判为 high、人工改为 medium，说明格式约束仍需配合业务评估。

Manual checks covered real analysis and human confirmation, automatic analysis after API submission, and a missing-key failure that returned `201 Created` with `analysis_failed`. Restoring the key allowed the same ticket to be retried successfully. Timeout and refusal handling is implemented but has not been separately simulated. A duplicate-charge example was classified as high priority and corrected to medium by a human, showing why schema constraints still need business-level evaluation.

## 第六天：追溯与简单评估 / Day 6: Traceability and evaluation

先增加模型名称、prompt 版本和分析时间三个字段，通过迁移更新数据库。成功分析时将这些信息与结果一起保存，并在 Admin 中只读显示；旧工单保持空值，不补造历史信息。

We added fields for the requested model name, prompt version, and analysis time, then migrated the database. Successful analysis saves this metadata with the result and displays it read-only in Admin. Older tickets retain empty values instead of invented historical metadata.

随后固定五条样例及预期标签，运行 v1：格式通过 5/5、分类匹配 5/5、优先级匹配 4/5。评估发现重复扣费的优先级偏高，以及回复中存在未确认的产品流程和行动声明。因此将 prompt 更新为 v2，明确优先级规则并限制无依据的承诺。

We defined five fixed cases and expected labels before running v1: 5/5 valid outputs, 5/5 category matches, and 4/5 priority matches. Review found an overly high duplicate-charge priority and unsupported product workflows and action claims. We updated the prompt to v2 with explicit priority rules and restrictions on unsupported commitments.

最后保留 v1 工单，用新工单重测重复扣费和团队中断：两条的格式与标签均通过，重复扣费改为 medium，中断回复不再声称已开始调查。七张评估工单的追溯信息均已保存。v2 是两条针对性回归结果，不代表完整五条或生产准确率；详情见 [评估记录](EVALUATION.md)。

We preserved the v1 tickets and reran duplicate-charge and outage cases as new v2 tickets. Both passed structure and label checks; duplicate-charge priority became medium, and the outage draft stopped claiming an investigation had begun. Metadata is saved for all seven evaluation tickets. These are two targeted v2 regression checks, not a full five-case or production accuracy result. See the [evaluation record](EVALUATION.md).

## 当前 Demo 流程 / Current demo flow

首页通过 API 提交工单 → 数据库保存 → 自动触发分析 → 验证并保存建议 → 页面展示结果 → Admin 人工修改并保存 → 明确确认。

Submit through the homepage and API → Persist in database → Automatically analyze → Validate and save suggestions → Display the result → Edit and save the human review in Admin → Explicitly confirm.

默认使用 mock 模式；设置 `TICKET_AI_MODE=openai` 并配置 `OPENAI_API_KEY` 后使用真实模型。Admin 新建的工单需手动触发分析。最终回复只保存，不发送给客户。

Mock mode is the default. Set `TICKET_AI_MODE=openai` and configure `OPENAI_API_KEY` to use the real model. Tickets created in Admin require manual analysis. Final replies are saved rather than sent to customers.

## 第七天：演示页面与项目收尾 / Day 7: Demo page and project handoff

先整理双语演示说明，包含三分钟流程、架构图、设计取舍和面试介绍。后端完整后，增加一页 Django 模板，配合 CSS 和原生 JavaScript 调用现有 API。页面展示运行模式、提交等待状态、分类、优先级、摘要和回复草稿，并提供 Admin 审核链接。使用 `textContent` 显示模型文字，提交期间禁用表单以减少重复操作。

We prepared a bilingual demo guide with a three-minute walkthrough, architecture, design tradeoffs, and an interview pitch. After completing the backend, we added one Django template with CSS and plain JavaScript against the existing API. It displays the analysis mode, submission progress, four analysis fields, and an Admin review link. Model text is rendered with `textContent`, and the form is disabled while submitting to reduce duplicate actions.

已通过首页提交真实发票请求，得到 billing / low 和待审核状态，并保存截图到 README。独立 mock 页面已验证空白输入提示、成功提交、结果展示和审核链接；这类流程检查不计入模型质量评估。

A live invoice request submitted through the homepage produced billing / low and a pending-review state; its screenshot is included in the README. Independent mock checks verified whitespace validation, successful submission, result display, and the review link. These workflow checks are separate from model-quality evaluation.

最后分别验证服务器停止时的网络错误提示，以及缺少 key 时“已保存但分析失败”的页面状态。失败工单可以从页面链接打开 Admin，标题和描述仍然保留，按钮恢复可用。本轮本地检查未调用付费模型；没有额外模拟超时或拒绝响应，也没有把前端样例算入固定评估集。

Final browser checks covered a stopped-server network error and the saved-but-analysis-failed state with a missing key. The failure ticket opens in Admin with its title and description preserved, and the submit button becomes available again. These local checks made no paid model requests; they did not separately simulate provider timeout or refusal, and frontend examples were not added to the fixed evaluation results.
