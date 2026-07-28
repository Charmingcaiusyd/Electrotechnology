# V3 Self Review And Optimization Recommendations

## Findings From My Pass

1. The V3 package reached 3000 questions, but it had 60 exact duplicate question prompts. V3.1 rewrites those duplicate prompts as scenario variants while keeping the total at 3000.
2. Multiple-choice answers were stored as answer text only. V3.1 adds `answer_key` and `answer_text` so later exam mode and auto-marking can work reliably.
3. Many distractors were too generic. V3.1 replaces weak E/F-style options with module-specific wrong choices.
4. `安全与合规边界` appeared inside detailed tags for every question. That makes knowledge-point analytics noisy. V3.1 moves it to `safety_boundary_note`.
5. Some generated questions use PDF source fragments that may come from neighbouring practical topics. V3.1 flags those with `source_domain_mismatch_possible`.
6. The old HTML rendered too much at once and had no page navigation. V3.1 adds pagination, test mode and per-card answer reveal.

## Remaining Work That Should Use DeepSeek

1. Semantic rewrite pass: ask a stronger DeepSeek model to rewrite high-risk questions flagged by `source_domain_mismatch_possible`.
2. Distractor calibration: generate closely matched distractors per exact concept, especially for AS/NZS, testing, motor control and protection calculation topics.
3. Difficulty calibration: mark each question as foundation, applied, integrated or fault-finding based on actual cognitive load, not generation cycle.
4. Source alignment pass: map each question to a more precise page/section/table/figure reference from the PDF.
5. Exam blueprint: split the 3000 questions into chapter practice, timed tests, weak-point review and final mock exams.

## Current V3.1 Metrics

```json
{
  "total": 3000,
  "by_module": {
    "S1": 300,
    "S10": 300,
    "S2": 300,
    "S3": 300,
    "S4": 300,
    "S5": 300,
    "S6": 300,
    "S7": 300,
    "S8": 300,
    "S9": 300
  },
  "by_type": {
    "fault_finding": 431,
    "multiple_choice": 1046,
    "scenario": 963,
    "short_answer": 560
  },
  "multiple_choice": {
    "count": 1046,
    "all_have_six_options": true,
    "answer_key_invalid": 0,
    "weak_generic_option_questions": 0
  },
  "missing_fields": {},
  "exact_duplicate_questions_after_pass": 0,
  "duplicate_seed_questions_rewritten_as_variants": 136,
  "generic_safety_concepts_in_detailed_tags": 0,
  "source_domain_mismatch_possible": 87,
  "top_primary_knowledge_points": [
    [
      "导管系统",
      229
    ],
    [
      "三相电机",
      204
    ],
    [
      "导体类型",
      154
    ],
    [
      "负载电流",
      152
    ],
    [
      "继电器线圈",
      151
    ],
    [
      "识图",
      143
    ],
    [
      "基材判断",
      134
    ],
    [
      "隔离验证",
      130
    ],
    [
      "测量精度",
      130
    ],
    [
      "工具状态",
      123
    ],
    [
      "连续性测试",
      119
    ],
    [
      "固定件选型",
      96
    ],
    [
      "电缆选型",
      92
    ],
    [
      "风险识别",
      91
    ],
    [
      "NO/NC 触点",
      63
    ],
    [
      "绝缘测试",
      63
    ],
    [
      "端接质量",
      62
    ],
    [
      "照明控制",
      61
    ],
    [
      "电缆结构",
      60
    ],
    [
      "测试记录",
      58
    ]
  ],
  "most_common_question_prefixes": [
    [
      "你在受监督的现场实训中处理 `风险管理流程`，需要把教材要求转化为可记录、可复查的作业步骤。 请围绕 `风险识别` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：根据学习材料，风险管理过程的第一步是什么？",
      1
    ],
    [
      "现场交底后，你负责整理 `风险管理流程` 的检查顺序，需要说明判断依据、测试条件和监督边界。 请围绕 `风险分析` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：风险评估中，“风险分析”的主要目的是什么？",
      1
    ],
    [
      "作为学徒，你正在准备 `风险管理流程` 的作业记录，需要把概念落实到隔离、检查、测量或排故动作。 请围绕 `控制措施` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：以下哪一项不是风险应对的选项？",
      1
    ],
    [
      "在开始安装或排故前，你需要确认 `风险管理流程` 的关键判断点，并说明错误做法会造成什么风险。 请围绕 `控制措施` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：为什么电气工作完成后必须审查行动方案的有效性？（简述两个原因）",
      1
    ],
    [
      "你正在复盘 `风险管理流程` 的训练任务，需要把答案写成能被主管检查的现场证据链。 请围绕 `风险识别` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：你被分配在拥挤的车间更换一个电机。请列出你应该采取的前三个风险管理行动。",
      1
    ],
    [
      "你在受监督的现场实训中处理 `风险管理流程`，需要把教材要求转化为可记录、可复查的作业步骤。 请围绕 `控制措施` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：根据学习材料，实施控制措施后下一步应做什么？",
      1
    ],
    [
      "现场交底后，你负责整理 `风险管理流程` 的检查顺序，需要说明判断依据、测试条件和监督边界。 请围绕 `风险识别` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：为什么在进行风险评估时，必须让所有相关人员参与？举两个理由。",
      1
    ],
    [
      "作为学徒，你正在准备 `风险管理流程` 的作业记录，需要把概念落实到隔离、检查、测量或排故动作。 请围绕 `风险识别` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：在一次风险评估中，针对更换照明灯具只记录了主电路隔离。但作业时，一名学徒因未放电的电容器而遭到轻微电击。分析风险评估过程出了什么问",
      1
    ],
    [
      "在开始安装或排故前，你需要确认 `风险管理流程` 的关键判断点，并说明错误做法会造成什么风险。 请围绕 `隔离验证` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：你作为学徒负责安全隔离一台泵电机以便维护。在行动之前，你应该参考哪些文件或记录？这与风险管理过程有何关联？",
      1
    ],
    [
      "你正在复盘 `风险管理流程` 的训练任务，需要把答案写成能被主管检查的现场证据链。 请围绕 `风险分析` 给出可执行判断，并说明需要哪些证据、记录和监督边界。 原题/种子问题：在风险分类中，哪种可能性与后果的组合通常会被评为高风险？",
      1
    ]
  ]
}
```
