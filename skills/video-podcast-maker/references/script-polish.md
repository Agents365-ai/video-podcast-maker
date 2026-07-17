# Script Polish — Deep Editing Toolkit

> **When to load:** After writing the first draft of `podcast.txt` (Step 4), **before** generating TTS (Step 8). Pair with [natural-narration.md](natural-narration.md) — natural-narration is the pre-write checklist (load it before writing); this file is the post-write editing toolkit (load it after the draft exists, to scrub remaining AI tells). Where the two conflict, natural-narration's spoken-narration rules win.
>
> **Sources:** Distilled and adapted for spoken scripts from `blader/humanizer` (33 patterns from Wikipedia's "Signs of AI writing"), `op7418/Humanizer-zh` (Chinese adaptation), `hardikpandya/stop-slop` (EN prose anti-slop), and `stop-slop-zh` (ZH scenario-gated editing).

## Contents

- [Editing Workflow](#editing-workflow) — the full draft → audit → polish loop
- [EN: Deep Pattern Catalog](#en-deep-pattern-catalog) — 12 patterns with before/after examples for spoken English
- [ZH: 深度模式目录](#zh-深度模式目录) — 12 patterns with before/after examples for spoken Chinese
- [Bilingual: Evidence Boundaries](#bilingual-evidence-boundaries) — when numbers and claims go too far
- [Quality Scoring](#quality-scoring) — per-language rubrics

---

## Editing Workflow

1. **Read the draft aloud.** Mark every line where you stumble, backtrack, or feel the cadence is off.
2. **Run the kill-list scan** (from natural-narration.md). Strike every kill-list word. Check the pre-delivery checklist.
3. **Pattern-audit** using the deep catalog below. For each hit, rewrite the affected sentence or paragraph.
4. **Evidence audit**: every number, stat, and factual claim must trace to Step 2 research (`topic_research.md`). See [Evidence Boundaries](#bilingual-evidence-boundaries).
5. **Read aloud again.** If any line still makes you wince, go back to step 3.
6. **Score** using the rubric below. Below 35/50 → revise; 35-42 → targeted fixes; 43+ → acceptable.

---

## EN: Deep Pattern Catalog

Each pattern shows the **Before** (AI-sounding), the **After** (natural spoken), and the **Fix** (what changed). These extend natural-narration.md's kill list with structural patterns that survive individual word cleanup.

### 1. Significance Inflation

Sentences that puff up importance instead of delivering facts.

**Before:** "The Statistical Institute was established in 1989, marking a pivotal moment in the evolution of regional statistics. This was part of a broader movement to decentralize administrative functions."

**After:** "The Statistical Institute opened in 1989 to collect and publish regional statistics independently from the national office."

**Fix:** Delete "marking a pivotal moment," "broader movement," "evolution of." State what the thing does.

### 2. Promotional / Ad Language

LLMs default to brochure-speak, especially for places, products, and cultural topics.

**Before:** "Nestled in the breathtaking hills of Tuscany, this vibrant village boasts a rich culinary heritage and stunning panoramic views."

**After:** "The village sits in the Tuscan hills. It's known for its wild boar ragu and a 12th-century church."

**Fix:** Delete "nestled," "breathtaking," "vibrant," "boasts," "stunning." Replace with specific, verifiable facts.

### 3. Vague Attribution

Attributing claims to unnamed authorities.

**Before:** "Experts believe this river plays a crucial role in the regional ecosystem."

**After:** "A 2019 Chinese Academy of Sciences survey found the river supports several endemic fish species."

**Fix:** Name the source + year + what they actually found. If you can't name one, drop the claim.

### 4. Formulaic "Challenges" Wrap-up

The AI tic of ending every topic description with a "despite challenges, future looks bright" paragraph.

**Before:** "Despite its prosperity, the city faces challenges including traffic and water scarcity. Nevertheless, with ongoing initiatives, it continues to thrive as an integral part of regional growth."

**After:** "Traffic worsened after 2015 when three IT parks opened. The city started a drainage project in 2022 to address floods."

**Fix:** Delete the "despite/nevertheless" sandwich. End on a concrete fact.

### 5. -ing Tail Inflation

Hanging participial phrases that add fake analytical depth.

**Before:** "The temple uses blue, green, and gold, symbolizing the region's natural beauty and reflecting the community's connection to the land."

**After:** "The temple uses blue, green, and gold. The architect said the colors reference local bluebonnets and the Gulf coast."

**Fix:** End the sentence at the fact. If you need the "why," make it a separate sentence with a named source.

### 6. Copula Avoidance

Replacing simple "is / are / has" with fancy verbs.

**Before:** "Gallery 825 serves as the organization's exhibition space. The gallery features four separate spaces and boasts over 3,000 square feet."

**After:** "Gallery 825 is the organization's exhibition space. It has four rooms totaling 3,000 square feet."

**Fix:** "is" beats "serves as." "has" beats "features." "has" beats "boasts." Every time.

### 7. Elegant Variation

Synonyms cycled to avoid repetition — a penalty-code artifact.

**Before:** "The protagonist faces challenges. The main character overcomes obstacles. The central figure triumphs. The hero returns."

**After:** "The protagonist faces many challenges, eventually triumphs, and returns home."

**Fix:** Repeat the plain word. It's fine spoken.

### 8. False Ranges

"Forcing ideas onto a fake scale with 'from X to Y'."

**Before:** "From the singularity of the Big Bang to the grand cosmic web, from star formation to the dance of dark matter — this book covers everything."

**After:** "The book covers the Big Bang, star formation, and current dark-matter theories."

**Fix:** Delete the "from X to Y" frame. List what's actually covered.

### 9. Persuasive Authority Tropes

Pretending to cut through noise to a deeper truth.

**Before:** "The real question is whether teams can adapt. At its core, the deeper issue is organizational readiness."

**After:** "The question is whether teams can adapt. That depends on whether the organization is ready to change."

**Fix:** "The real question" → "The question." "At its core" → delete. "What really matters" → delete.

### 10. Manufactured Punchlines

Stacking short declarative sentences to sound dramatic.

**Before:** "Then the new system arrived. No training data. No human priors. No aesthetic assumptions. The old rules dissolved."

**After:** "The new system worked differently because it had no training data and no built-in assumptions about what looks good. That made the older methods less useful."

**Fix:** Merge staccato fragments into sentences that explain. One short sentence for emphasis is fine; four in a row is a tell.

### 11. Aphorism Formulas

Turning ordinary claims into reusable profundities.

**Before:** "Symmetry is the language of trust. Efficiency becomes a trap when teams forget the human layer."

**After:** "Symmetric layouts feel more predictable to users. Teams can over-optimize and miss how people actually use the tool."

**Fix:** Replace "X is the Y of Z" with concrete observation. Replace "X becomes a trap" with what actually happens.

### 12. Generic Uplift Endings

Vague positive conclusions that say nothing.

**Before:** "The future looks bright. Exciting times lie ahead as the company continues its journey toward excellence."

**After:** "The company plans to open two more locations next year."

**Fix:** End on a concrete fact, a specific number, or a plain question. Never "future looks bright" or "time will tell."

---

## ZH: 深度模式目录

每个模式展示改写前（AI味）、改写后（自然口语）和修改要点。这些补充 natural-narration.md 的删除清单，覆盖单词替换无法解决的深层结构问题。

### 1. 意义膨胀

夸大重要性而非陈述事实。

**改写前：** "加泰罗尼亚统计局于 1989 年正式成立，标志着西班牙区域统计演变史上的关键时刻。这一举措是全国范围内更广泛运动的一部分，旨在分散行政职能。"

**改写后：** "加泰罗尼亚统计局 1989 年成立，负责独立于国家统计局收集和发布区域数据。"

**修改：** 删除"标志着关键时刻""更广泛运动的一部分""旨在"。直接说它做什么。

### 2. 宣传腔

LLM 对地点、产品、文化话题默认使用旅游手册式语言。

**改写前：** "坐落于令人叹为观止的贡德尔地区，这座充满活力的城镇拥有丰富的文化遗产和迷人的自然美景。"

**改写后：** "这座城镇在埃塞俄比亚贡德尔地区，以每周集市和一座 18 世纪教堂出名。"

**修改：** 删除"坐落于""令人叹为观止""充满活力的""拥有丰富的""迷人的"。全部替换为可验证的具体事实。

### 3. 模糊归因

将观点归于不具名的权威。

**改写前：** "专家认为这条河在区域生态系统中发挥着至关重要的作用。"

**改写后：** "中科院 2019 年调查显示，这条河支持多种特有鱼类。"

**修改：** 说出机构名称 + 年份 + 他们实际发现了什么。说不出来源就删掉这句话。

### 4. 名词化动词壳

用"进行/实现/做出 + 抽象名词"代替直接动词。

| 避免 | 改为 |
| ------ | ------ |
| 进行优化 | 优化了哪里 |
| 实现增长 | 涨了多少 |
| 做出选择 | 选了哪个 |
| 提供保障 | 谁负责什么 |
| 采取措施 | 具体做了什么 |
| 赋能业务 | 帮哪个岗位省了什么 |

**改写前：** "新系统对工作流程进行了优化，实现了效率的大幅提升。"

**改写后：** "新系统把审批从三步改成一步。客服每天少处理 40 张重复工单。"

**修改：** 每个名词化动词替换为具体的动作 + 可感知的结果。

### 5. 抽象主体做人的事

让"时代""科技""AI""市场""数据"充当主语做人的动作。

| 避免 | 改为 |
| ------ | ------ |
| 时代呼唤创新 | 开发者需要更快的工具 |
| AI 赋能创作 | 设计师用 AI 一天出了 30 版方案 |
| 市场正在奖励高效团队 | 去年融资最多的三家创业公司都不到 15 人 |
| 数据告诉我们用户更喜欢简单 | 4 月改版后留存率从 31% 升到 45% |

**修改：** 说出谁、做了什么、结果是什么。如果说不出来，删掉这句话。

### 6. 三段式平衡

强行把观点塞进"是...，是...，更是..."或"既要...又要...还要..."的模具。

**改写前：** "AI 不仅是工具，更是伙伴，更是未来生产力的入口。"

**改写后：** "团队把 AI 当工具用：写测试、查日志、整理客服问题。目前没有一个人把它当'伙伴'。"

**修改：** 保留最有信息量的一项，用具体例子替换排比。两项优于三项。

### 7. 否定式对比

"不是 X，而是 Y"——AI 最爱的戏剧化转折。

**改写前：** "这不是一次普通的更新，而是一场生产力的革命。"

**改写后：** "这次更新加了批处理、键盘快捷键和离线模式。测试用户反馈：任务完成更快了。"

**修改：** 直接说 Y。对比只在 X 和 Y 有真实信息差时才需要，否则就是演戏。

### 8. 口号式结尾

段末突然拔高。

**删除清单：**

- 这，就是……的力量
- 唯有……，方能……
- 未来可期
- 让我们一起，向着……前进
- 为……注入新的活力
- 值得期待 / 让我们拭目以待

**改写前：** "这次合作将为中国市场注入新的活力。让我们拭目以待。"

**改写后：** "两家公司计划明年一季度推出联名产品，价格尚未公布。"

**修改：** 段末落在一个具体事实上——数字、日期、名称、下一步动作。

### 9. 元结构标记

宣告结构而非推进内容。

**删除清单：**

- 接下来我将、本文将、下面我们来看
- 值得注意的是、值得一提的是、不得不说
- 首先/其次/最后（仅作为结构宣告时）
- 总的来说、综上所述、由此可见

**修改：** 直接讲下一件事。听众不需要知道"现在进入第三部分"——他们能听出来。

### 10. 空洞程度词

用"非常、十分、极其、显著、大幅"代替具体数字。

| 避免 | 改为 |
| ------ | ------ |
| 显著提升 | 从 4.2 秒降到 0.8 秒 |
| 大幅减少 | 从 30 条降到 2 条 |
| 非常重要 | 影响审批能不能通过 |
| 很有帮助 | 每周少做 3 小时重复工作 |

**修改：** 每个程度词替换为数字或可感知的后果。

### 11. 聊天机器人残留

AI 对话语气混入稿件。

**删除清单：**

- 当然可以、好的、没问题
- 希望这对你有帮助
- 下面是、以下是、我将为你……
- 作为一个 AI、根据我的训练数据

**修改：** 这些永远不会出现在人类写的播客稿里。直接删。

### 12. 假精确数字

AI 编造的看起来很精确的数字。

**改写前：** "该产品上市后用户满意度提升了 92%，复购率达到 4.1 倍。"

**改写后：** "早期用户反馈正面，但公司尚未公布官方数据。"

**修改：** 每一个数字必须能从 `topic_research.md` 追溯。说不出来源的数字就是编的。删掉或标注"根据官方公布数据"。

---

## Bilingual: Evidence Boundaries

Applies to both EN and ZH scripts. Before keeping any claim in the narration, check:

| Claim type | Minimum bar |
| ------------ | ------------- |
| Numbers (percentages, multiples, counts) | Must be in `topic_research.md` with a source |
| Causal claims ("X caused Y," "X leads to Y") | Source must demonstrate causation, not just correlation |
| Market / demand claims ("strong demand," "users want") | Must cite specific data: sales, surveys, waitlist numbers |
| Competitive claims ("best," "fastest," "only") | Must cite a benchmark, award, or independent review |
| Future predictions ("will," "is expected to") | Must attribute to a named forecaster or label as speculation |

**Weak → Strong:**

| Weak (AI default) | Strong (evidence-backed) |
| --- | --- |
| 48 万美元众筹验证了市场需求 | 48 万美元说明早期用户愿意付费。大众市场接受度尚未验证。 |
| The tool dramatically improved productivity | Teams using the tool reported 30% fewer meetings, according to the company's Q3 survey |
| 被广泛认为是行业最佳 | 在 G2 2024 年夏季报告中，该产品在三个类别排名第一 |

**When evidence is thin:** narrow the claim. "这说明早期兴趣，但不能证明大众需求" beats "这充分验证了市场前景."

---

## Quality Scoring

### EN Rubric (/50)

| Dimension | Question | Score |
| ----------- | ---------- | ------- |
| Directness | States facts or announces them? | /10 |
| Rhythm | Sentence lengths varied? No staccato stacks? | /10 |
| Trust | Respects listener? No over-explaining? | /10 |
| Authenticity | Sounds like a person talking? | /10 |
| Density | Anything left to cut? | /10 |

### ZH Rubric (/50)

| 维度 | 评估标准 | 得分 |
| ------ | ---------- | ------ |
| 直接性 | 陈述事实还是宣告事实？ | /10 |
| 节奏 | 句子长短交错？没有连续短句堆叠？ | /10 |
| 具体性 | 有具体的动作、数字、场景或来源吗？ | /10 |
| 自然度 | 像人在说话，而非机器朗读？ | /10 |
| 精炼度 | 还有可删的吗？ | /10 |

**Below 35/50:** revise before TTS. **35-42:** targeted fixes on lowest-scoring dimensions. **43+:** acceptable.
