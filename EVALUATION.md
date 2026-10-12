# 简单评估 / Simple Evaluation

五条固定样例用于检查格式和业务判断，不代表生产环境准确率。预期标签在运行前确定；逐条记录真实模型结果，不用人工修改后的值计算模型得分。

These five fixed cases check output structure and business judgment, not production accuracy. Expected labels are defined before execution. Score the original model output, not the human-corrected values.

## 优先级规则 / Priority rubric

- **low:** 一般咨询、记录请求或建议，没有服务中断。 / Routine questions, record requests, or suggestions without service disruption.
- **medium:** 单个用户的账单或部分功能问题，需要处理，但没有大范围核心服务中断。 / Individual billing or partial-function problems that need attention without a widespread core-service outage.
- **high:** 大范围核心服务不可用或紧急安全问题。 / Widespread loss of core service or an urgent security issue.

## 固定样例 / Fixed cases

| Case | Expected category | Expected priority | Ticket ID | Actual category | Actual priority | Model / prompt version | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01 — Invoice copy | billing | low | 9 | billing | low | gpt-4.1-mini / v1 | Labels pass; draft needs review |
| 02 — Duplicate charge | billing | medium | 11 | billing | high | gpt-4.1-mini / v1 | Category passes; priority mismatch |
| 03 — Account email question | account | low | 12 | account | low | gpt-4.1-mini / v1 | Labels pass; draft needs review |
| 04 — Widespread outage | technical | high | 13 | technical | high | gpt-4.1-mini / v1 | Labels pass; unsupported action claims |
| 05 — Feature suggestion | other | low | 14 | other | low | gpt-4.1-mini / v1 | Labels pass; forwarding promise needs approval |

### 01 — Invoice copy

**Title:** Need a copy of my subscription invoice

**Description:** Could you send me a copy of my invoice for this month's subscription? My payment went through successfully and my account works normally. I need the invoice for my expense records.

### 02 — Duplicate charge

**Title:** Charged twice for my monthly subscription

**Description:** My monthly subscription costs $20, but I noticed two $20 charges on my card today. My account still works normally. Could you check whether one of the charges was a mistake and explain how I can request a refund?

### 03 — Account email question

**Title:** How can I change my account email address?

**Description:** I can sign in and use my account normally. I would like to change the email address associated with my account. Could you explain the steps?

### 04 — Widespread outage

**Title:** Service unavailable for our entire team

**Description:** Every member of our team gets a server error when opening the service. Nobody can access any of the main features, and our work has been blocked for two hours. Please investigate urgently.

### 05 — Feature suggestion

**Title:** Suggestion to add dark mode

**Description:** The service works normally. I would like to suggest a dark mode option because I often use the app at night. This is a feature suggestion, not a current service problem.

## 记录方法 / Recording procedure

1. 在 openai 模式下通过 API 提交，每条先运行一次。 / Submit through the API in openai mode, once per case initially.
2. 记录工单 ID 和原始 `ai_result` 中的标签，核对四个字段存在且文本非空。 / Record the ticket ID and labels from the original `ai_result`; check all four fields and non-empty text.
3. 在 Admin 核对模型、prompt 版本和分析时间。 / Check the model, prompt version, and analysis time in Admin.
4. 人工检查摘要是否忠实、回复是否包含无依据的政策或完成操作的声明。 / Check summary accuracy and unsupported policy or completed-action claims in the draft.
5. 修改 prompt 时更新版本，保留此前结果并另记新一轮。 / Version prompt changes and record a separate round while preserving earlier results.

v1 本轮已完成 5/5：格式通过 5/5，分类匹配 5/5，优先级匹配 4/5。回复草稿由人工定性检查；其中存在未确认的流程和行动承诺，因此标签通过不等于回复可以直接发送。

The v1 round is complete: 5/5 valid outputs, 5/5 category matches, and 4/5 priority matches. Reply drafts were reviewed qualitatively. Unverified workflows and action commitments were observed, so matching labels do not make a draft ready to send.

## 观察记录 / Review notes

- **Case 01 / Ticket 9:** 模型和 prompt 版本已保存，分析时间为 `2026-10-12 19:11:52 UTC`。摘要忠实；回复假设可以取出发票并发送到注册邮箱，但这些操作流程尚未提供，需要人工审核并改进 prompt。
- **Case 01 / Ticket 9:** Model and prompt version were persisted, with analysis time `2026-10-12 19:11:52 UTC`. The summary is accurate. The draft assumes invoice retrieval and delivery to a registered email address without a provided workflow; this needs human review and a prompt improvement.
- **Case 02 / Ticket 11:** 追溯信息齐全，分析时间为 `2026-10-12 19:15:55 UTC`。分类和摘要正确，但单个用户的重复扣费被判为 high，而预设规则要求 medium。回复未声称已经退款，但承诺账户核查和后续更新，仍需由审核人确认是否可执行。
- **Case 02 / Ticket 11:** Metadata is complete, with analysis time `2026-10-12 19:15:55 UTC`. Category and summary are accurate, but an individual duplicate charge was rated high rather than the rubric's medium. The reply does not claim a completed refund; its account-review and follow-up commitments still require reviewer approval.
- **Case 03 / Ticket 12:** 分类、优先级和摘要符合预期。回复建议在账户设置中更新邮箱，但未提供此产品的真实设置路径，需要人工核实。
- **Case 03 / Ticket 12:** Category, priority, and summary match expectations. The draft suggests updating the email in account settings without a supplied product workflow; those steps need human verification.
- **Case 04 / Ticket 13:** 分类、优先级和摘要符合预期。回复声称工程师正在调查并恢复服务，但输入没有提供这些行动事实，必须在确认前改写。
- **Case 04 / Ticket 13:** Category, priority, and summary match expectations. The draft claims engineers are investigating and restoring service without evidence of those actions; it must be revised before confirmation.
- **Case 05 / Ticket 14:** 分类、优先级和摘要符合预期。回复承诺把建议转交开发团队，但目前没有此操作，需要审核人确认后才能保留该承诺。
- **Case 05 / Ticket 14:** Category, priority, and summary match expectations. The forwarding promise needs reviewer approval because the demo has no action that sends feedback to a development team.

## v2 改进与针对性回归 / v2 improvement and targeted regression

v2 已把上述优先级规则明确写入 prompt，并要求回复不编造产品步骤、政策、正在进行的行动或未来承诺。重新运行 Case 02 和 Case 04，记录针对性回归结果；这不是完整五条样例的 v2 得分。

v2 explicitly includes the priority rubric and prohibits invented product steps, policies, ongoing actions, and future commitments. Cases 02 and 04 are rerun as targeted regression checks. Their results do not represent a full five-case v2 score.

| Case | Ticket ID | Expected labels | Actual labels | Model / prompt version | Result |
| --- | --- | --- | --- | --- | --- |
| 02 — Duplicate charge | 15 | billing / medium | billing / medium | gpt-4.1-mini / v2 | Labels pass; draft improved |
| 04 — Widespread outage | 16 | technical / high | technical / high | gpt-4.1-mini / v2 | Labels pass; unsupported action claims removed |

Case 02 的优先级从 v1 的 high 修正为 medium。v2 回复先询问扣费日期与交易编号，未声称已开始调查或已退款；其中后续协助的表述仍需人工确认。Case 04 保持 technical / high，回复改为询问时区和具体错误信息，不再声称工程师正在调查或修复。两条回归的格式、分类、优先级和追溯信息均通过。

Case 02's priority changed from v1's high to medium. The v2 draft asks for charge dates and transaction references without claiming an investigation or refund has already occurred. Its conditional follow-up wording still requires human approval. Case 04 remains technical / high and asks for a time zone and error details instead of claiming engineers are already investigating or fixing the issue. Both targeted cases passed structure, category, priority, and metadata checks.

v2 仅运行了上述两条，尚未重新运行其余三条。这是对已观察问题的针对性检查，不能解释为完整样例集或真实工单的 100% 准确率。数据库核对确认七张评估工单的原始结果和追溯字段均已保存。

Only these two cases were rerun with v2; the other three have not been rerun. These targeted checks do not establish 100% accuracy across the full set or real tickets. Database checks confirmed that all seven evaluation tickets retain their original outputs and metadata.
