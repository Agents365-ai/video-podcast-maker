# Chinese Polyphone Reference (zh-CN)

> **When to load:** Only during Step 4.5 (Pronunciation Pre-Flight) for zh-CN videos. Reading this whole table for any other purpose wastes context.

This is a non-exhaustive reference for the most common polyphones in tech / explainer videos. Use it as a starting checklist while scanning `podcast.txt`; rely on linguistic judgment for words not listed here.

## Decision rules

- Pick the pronunciation by **context**, not by single-character lookup. Polyphone disambiguation is what makes this an LLM step instead of a regex.
- Add **whole-word** entries to `videos/{name}/phonemes.json`, never single characters. Whole-word keys avoid catastrophic over-replacement (the applier matches longest-first).
- Skip any word **already** present in the global `${SKILL_DIR}/phonemes.json` — duplicate entries waste a phoneme tag and risk drift.

## Common polyphones in tech / explainer content

| 字 | Pinyin choices | Typical context |
|----|---|---|
| 行 | háng / xíng | 一行/银行/行业 (háng); 执行/运行/可行/行走 (xíng) |
| 重 | chóng / zhòng | 重做/重新/重复/重试 (chóng); 重要/重量/严重 (zhòng) |
| 长 | cháng / zhǎng | 长度/长期 (cháng); 增长/成长/校长 (zhǎng) |
| 为 | wéi / wèi | 作为/认为/成为 (wéi); 因为/为了 (wèi) |
| 还 | hái / huán | 还有/还是 (hái); 归还/偿还 (huán) |
| 着 | zhe / zháo / zhuó | 跟着/沿着 (zhe); 着火/着急 (zháo); 着手/着重 (zhuó) |
| 差 | chā / chà / chāi | 差别/差距 (chā); 差不多 (chà); 出差 (chāi) |
| 调 | diào / tiáo | 调研/调查/语调 (diào); 调整/协调 (tiáo) |
| 分 | fēn / fèn | 分钟/分开/分类 (fēn); 缘分/部分/养分 (fèn) |
| 中 | zhōng / zhòng | 中间/中央 (zhōng); 中奖/命中 (zhòng) |
| 处 | chǔ / chù | 处理/相处 (chǔ); 到处/好处 (chù) |
| 间 | jiān / jiàn | 中间/时间/期间 (jiān); 间隔/间断 (jiàn) |
| 给 | gěi / jǐ | 给我/给你 (gěi); 供给/补给 (jǐ) |
| 教 | jiāo / jiào | 教书/教课 (jiāo); 教育/宗教 (jiào) |
| 模 | mó / mú | 模型/模式/规模 (mó); 模样/一模一样 (mú) |
| 量 | liàng / liáng | 数量/质量/分量 (liàng); 测量/丈量 (liáng) |
| 觉 | jué / jiào | 感觉/觉得 (jué); 睡觉/午觉 (jiào) |
| 应 | yīng / yìng | 应该/应当 (yīng); 答应/反应/适应 (yìng) |
| 干 | gān / gàn | 干净/相干 (gān); 干活/能干 (gàn) |
| 转 | zhuǎn / zhuàn | 转弯/转换 (zhuǎn); 转动/旋转 (zhuàn) |
| 划 | huá / huà | 划船/划算 (huá); 计划/规划 (huà) |
| 数 | shù / shǔ | 数字/次数 (shù); 数数/数一数 (shǔ) |
| 当 | dāng / dàng | 当然/应当 (dāng); 适当/上当 (dàng) |
| 占 | zhān / zhàn | 占卜 (zhān); 占据/占领 (zhàn) |
| 假 | jiǎ / jià | 假如/假设/假装 (jiǎ); 放假/假期 (jià) |
| 倒 | dǎo / dào | 倒下/倒闭 (dǎo); 倒车/倒影/倒是 (dào) |
| 几 | jī / jǐ | 几乎/茶几 (jī); 几个/几次 (jǐ) |
| 卡 | kǎ / qiǎ | 卡片/打卡 (kǎ); 卡住/关卡 (qiǎ) |

## Pinyin format requirements

- Use **tone marks** (ā á ǎ à), space-separated syllables: `"一行命令": "yì háng mìng lìng"`.
- Never use bare single-character keys like `"行": "háng"`.
- The TTS layer converts tone-marked pinyin to SAPI numeric tones automatically; you don't need to do that conversion yourself.
