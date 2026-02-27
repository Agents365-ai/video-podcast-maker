#!/usr/bin/env python3
"""
Polyphone Database for Chinese TTS
Common multi-reading characters with context-based pronunciation rules
"""

# Format: { character: { default: pinyin, contexts: { pinyin: [words] } } }
POLYPHONE_DATABASE = {
    "行": {
        "default": "xíng",
        "contexts": {
            "háng": ["一行", "几行", "行列", "行号", "单行", "多行", "换行", "命令行", "代码行", "行数", "行业", "银行", "同行", "内行", "外行"],
            "xíng": ["执行", "运行", "并行", "发行", "流行", "行为", "行动", "可行", "施行", "践行", "通行", "行程", "行走", "行驶"],
        }
    },
    "重": {
        "default": "zhòng",
        "contexts": {
            "chóng": ["重新", "重做", "重复", "重启", "重试", "重载", "重建", "重构", "重写", "重现", "重叠", "重来", "重跑", "重装"],
            "zhòng": ["重要", "重点", "重量", "严重", "重大", "重视", "加重", "轻重", "比重", "权重", "注重"],
        }
    },
    "长": {
        "default": "cháng",
        "contexts": {
            "zhǎng": ["成长", "增长", "生长", "长大", "长辈", "长官", "部长", "首长", "班长", "组长", "队长", "会长", "市长", "校长"],
            "cháng": ["长度", "长期", "长时间", "超长", "漫长", "延长", "最长", "长短", "长久", "长远", "长处", "特长"],
        }
    },
    "载": {
        "default": "zài",
        "contexts": {
            "zǎi": ["下载", "上载", "转载", "刊载", "下载量", "下载速度", "下载链接"],
            "zài": ["记载", "载入", "承载", "负载", "搭载", "装载", "满载", "过载", "载体", "载荷"],
        }
    },
    "调": {
        "default": "diào",
        "contexts": {
            "tiáo": ["调整", "调节", "微调", "协调", "调试", "调配", "调和", "调解", "调剂", "空调", "调皮"],
            "diào": ["调用", "调度", "音调", "曲调", "基调", "格调", "情调", "回调", "强调", "语调", "声调"],
        }
    },
    "数": {
        "default": "shù",
        "contexts": {
            "shǔ": ["数一数二", "数不清", "数数", "倒数", "屈指可数"],
            "shù": ["数字", "数据", "数量", "数组", "参数", "变数", "系数", "常数", "基数", "指数", "函数", "奇数", "偶数", "整数", "小数"],
        }
    },
    "差": {
        "default": "chà",
        "contexts": {
            "chā": ["差异", "差距", "差别", "偏差", "误差", "温差", "时差", "落差", "价差", "差值", "差分"],
            "chà": ["差不多", "差劲", "差点", "差一点", "很差", "太差"],
            "chāi": ["出差", "差事", "差遣"],
        }
    },
    "传": {
        "default": "chuán",
        "contexts": {
            "zhuàn": ["传记", "自传", "列传", "外传", "水浒传"],
            "chuán": ["传输", "传递", "传播", "传送", "传达", "遗传", "流传", "宣传", "传统", "传承", "传感器", "传真"],
        }
    },
    "分": {
        "default": "fēn",
        "contexts": {
            "fèn": ["部分", "成分", "身分", "分内", "分外", "本分", "过分", "充分", "分量"],
            "fēn": ["分类", "分析", "分布", "分割", "分开", "分离", "分裂", "分配", "分享", "分支", "分段", "分词", "分页", "分钟", "区分", "划分", "拆分"],
        }
    },
    "量": {
        "default": "liàng",
        "contexts": {
            "liáng": ["量一量", "测量", "量体温", "量身", "量度"],
            "liàng": ["数量", "质量", "流量", "容量", "能量", "变量", "常量", "向量", "增量", "存量", "总量", "批量", "海量", "大量", "少量"],
        }
    },
    "度": {
        "default": "dù",
        "contexts": {
            "duó": ["揣度", "测度", "忖度", "度德量力"],
            "dù": ["速度", "精度", "程度", "角度", "维度", "深度", "高度", "长度", "宽度", "温度", "湿度", "亮度", "灵敏度"],
        }
    },
    "模": {
        "default": "mó",
        "contexts": {
            "mú": ["模样", "模子", "模具", "模板"],
            "mó": ["模型", "模式", "模块", "模拟", "模仿", "规模", "模糊", "模范", "模组", "大模型", "小模型", "语言模型"],
        }
    },
    "乐": {
        "default": "lè",
        "contexts": {
            "yuè": ["音乐", "乐曲", "乐器", "乐谱", "乐队", "乐团", "声乐", "器乐", "民乐", "摇滚乐", "交响乐"],
            "lè": ["快乐", "乐趣", "乐观", "可乐", "欢乐", "娱乐", "安乐"],
        }
    },
    "的": {
        "default": "de",
        "contexts": {
            "dí": ["的确", "的当", "目的", "标的", "众矢之的"],
            "dì": ["目的地", "目的性"],
        }
    },
    "了": {
        "default": "le",
        "contexts": {
            "liǎo": ["了解", "了然", "了结", "一目了然", "不了了之", "明了"],
        }
    },
    "为": {
        "default": "wéi",
        "contexts": {
            "wèi": ["为了", "因为", "为什么", "为何", "为此"],
            "wéi": ["作为", "成为", "认为", "以为", "行为", "人为"],
        }
    },
    "处": {
        "default": "chù",
        "contexts": {
            "chǔ": ["处理", "处置", "处于", "相处", "处境"],
            "chù": ["之处", "用处", "好处", "到处", "四处", "住处", "去处", "深处", "远处"],
        }
    },
    "发": {
        "default": "fā",
        "contexts": {
            "fà": ["头发", "毛发", "理发", "白发", "发型"],
            "fā": ["发送", "发布", "发展", "发现", "发生", "发起", "发表", "发明", "开发", "研发", "触发", "激发", "并发"],
        }
    },
    "称": {
        "default": "chēng",
        "contexts": {
            "chèn": ["对称", "匀称", "称心", "称职", "相称"],
            "chēng": ["名称", "称为", "称作", "称呼", "称号", "简称", "俗称", "总称"],
        }
    },
    "识": {
        "default": "shí",
        "contexts": {
            "zhì": ["标识", "识别码"],
            "shí": ["认识", "知识", "意识", "识别", "共识", "常识", "见识", "学识"],
        }
    },
    "空": {
        "default": "kōng",
        "contexts": {
            "kòng": ["空白", "空格", "空缺", "空闲", "有空", "抽空", "填空"],
            "kōng": ["空间", "天空", "空气", "空中", "航空", "太空", "真空", "空调"],
        }
    },
    "更": {
        "default": "gèng",
        "contexts": {
            "gēng": ["更新", "更改", "更换", "更替", "更正", "变更"],
            "gèng": ["更加", "更好", "更多", "更快", "更高", "更强", "更大"],
        }
    },
    "相": {
        "default": "xiāng",
        "contexts": {
            "xiàng": ["相机", "相片", "照相", "真相", "相貌", "长相", "首相", "丞相"],
            "xiāng": ["相关", "相同", "相似", "相比", "相对", "互相", "相信", "相当", "相互"],
        }
    },
    "系": {
        "default": "xì",
        "contexts": {
            "jì": ["系上", "系紧", "系鞋带"],
            "xì": ["系统", "系列", "关系", "联系", "体系", "操作系统", "文件系统", "星系"],
        }
    },
    "解": {
        "default": "jiě",
        "contexts": {
            "xiè": ["解数", "浑身解数"],
            "jiě": ["解决", "解析", "解释", "解码", "解压", "解密", "理解", "分解", "讲解", "了解", "化解"],
        }
    },
    "率": {
        "default": "lǜ",
        "contexts": {
            "shuài": ["率领", "率先", "效率", "轻率", "坦率", "草率"],
            "lǜ": ["比率", "概率", "频率", "速率", "利率", "汇率", "税率", "功率", "准确率", "命中率", "成功率"],
        }
    },
    "间": {
        "default": "jiān",
        "contexts": {
            "jiàn": ["间隔", "间断", "间接", "间歇", "中间人"],
            "jiān": ["时间", "空间", "之间", "期间", "中间", "房间", "车间", "瞬间", "民间", "人间"],
        }
    },
    "切": {
        "default": "qiē",
        "contexts": {
            "qiè": ["一切", "切身", "切实", "亲切", "密切", "迫切", "急切", "恳切"],
            "qiē": ["切割", "切分", "切换", "切片", "切入", "切断"],
        }
    },
    "省": {
        "default": "shěng",
        "contexts": {
            "xǐng": ["反省", "省悟", "省亲", "内省"],
            "shěng": ["省份", "省略", "省去", "节省", "省事", "省心", "省力"],
        }
    },
    "便": {
        "default": "biàn",
        "contexts": {
            "pián": ["便宜", "大腹便便"],
            "biàn": ["方便", "便于", "便利", "便捷", "顺便", "随便", "即便"],
        }
    },
    "应": {
        "default": "yìng",
        "contexts": {
            "yīng": ["应该", "应当", "应有", "应然"],
            "yìng": ["响应", "应用", "应答", "适应", "对应", "反应", "效应", "应变", "应急"],
        }
    },
    "还": {
        "default": "hái",
        "contexts": {
            "huán": ["还原", "归还", "偿还", "返还", "交还"],
            "hái": ["还是", "还有", "还要", "还能", "还会"],
        }
    },
    "卷": {
        "default": "juàn",
        "contexts": {
            "juǎn": ["卷起", "卷入", "卷曲", "花卷", "蛋卷"],
            "juàn": ["卷轴", "卷宗", "试卷", "问卷", "答卷", "画卷"],
        }
    },
    "强": {
        "default": "qiáng",
        "contexts": {
            "qiǎng": ["勉强", "强迫", "强求", "强人所难"],
            "jiàng": ["倔强", "强嘴"],
            "qiáng": ["强大", "强调", "加强", "增强", "强化", "强劲", "强烈", "坚强", "顽强"],
        }
    },
    "背": {
        "default": "bèi",
        "contexts": {
            "bēi": ["背包", "背负", "背着"],
            "bèi": ["背景", "背后", "背面", "后背", "背诵", "违背"],
        }
    },
    "折": {
        "default": "zhé",
        "contexts": {
            "shé": ["折本", "折耗"],
            "zhē": ["折腾", "翻折"],
            "zhé": ["折扣", "折叠", "折线", "打折", "曲折", "挫折", "转折"],
        }
    },
}


# Full word pronunciations for common polyphone words
WORD_PRONUNCIATIONS = {
    # 行 words
    "一行": "yì háng", "几行": "jǐ háng", "行列": "háng liè", "行号": "háng hào",
    "单行": "dān háng", "多行": "duō háng", "换行": "huàn háng", "命令行": "mìng lìng háng",
    "代码行": "dài mǎ háng", "行数": "háng shù", "行业": "háng yè", "银行": "yín háng",
    "同行": "tóng háng", "内行": "nèi háng", "外行": "wài háng",
    "执行": "zhí xíng", "运行": "yùn xíng", "并行": "bìng xíng", "发行": "fā xíng",
    "流行": "liú xíng", "行为": "xíng wéi", "行动": "xíng dòng", "可行": "kě xíng",
    "施行": "shī xíng", "践行": "jiàn xíng", "通行": "tōng xíng", "行程": "xíng chéng",
    # 重 words
    "重新": "chóng xīn", "重做": "chóng zuò", "重复": "chóng fù", "重启": "chóng qǐ",
    "重试": "chóng shì", "重载": "chóng zài", "重建": "chóng jiàn", "重构": "chóng gòu",
    "重写": "chóng xiě", "重现": "chóng xiàn", "重叠": "chóng dié", "重来": "chóng lái",
    "重要": "zhòng yào", "重点": "zhòng diǎn", "重量": "zhòng liàng", "严重": "yán zhòng",
    "重大": "zhòng dà", "重视": "zhòng shì", "加重": "jiā zhòng", "权重": "quán zhòng",
    # 长 words
    "成长": "chéng zhǎng", "增长": "zēng zhǎng", "生长": "shēng zhǎng", "长大": "zhǎng dà",
    "长辈": "zhǎng bèi", "部长": "bù zhǎng", "首长": "shǒu zhǎng",
    "长度": "cháng dù", "长期": "cháng qī", "长时间": "cháng shí jiān", "超长": "chāo cháng",
    "漫长": "màn cháng", "延长": "yán cháng", "最长": "zuì cháng",
    # 载 words
    "下载": "xià zǎi", "上载": "shàng zǎi", "转载": "zhuǎn zǎi", "刊载": "kān zǎi",
    "下载量": "xià zǎi liàng", "下载速度": "xià zǎi sù dù", "下载链接": "xià zǎi liàn jiē",
    "记载": "jì zài", "载入": "zài rù", "承载": "chéng zài", "负载": "fù zài",
    "搭载": "dā zài", "装载": "zhuāng zài", "满载": "mǎn zài", "过载": "guò zài",
    # 调 words
    "调整": "tiáo zhěng", "调节": "tiáo jié", "微调": "wēi tiáo", "协调": "xié tiáo",
    "调试": "tiáo shì", "调配": "tiáo pèi", "空调": "kōng tiáo",
    "调用": "diào yòng", "调度": "diào dù", "音调": "yīn diào", "曲调": "qǔ diào",
    "回调": "huí diào", "强调": "qiáng diào", "语调": "yǔ diào",
    # 数 words
    "数字": "shù zì", "数据": "shù jù", "数量": "shù liàng", "数组": "shù zǔ",
    "参数": "cān shù", "变数": "biàn shù", "系数": "xì shù", "常数": "cháng shù",
    "基数": "jī shù", "指数": "zhǐ shù", "函数": "hán shù", "奇数": "jī shù",
    "偶数": "ǒu shù", "整数": "zhěng shù", "小数": "xiǎo shù",
    # 差 words
    "差异": "chā yì", "差距": "chā jù", "差别": "chā bié", "偏差": "piān chā",
    "误差": "wù chā", "温差": "wēn chā", "时差": "shí chā", "落差": "luò chā",
    "差值": "chā zhí", "差分": "chā fēn",
    "差不多": "chà bu duō", "差劲": "chà jìn", "差点": "chà diǎn",
    # 传 words
    "传输": "chuán shū", "传递": "chuán dì", "传播": "chuán bō", "传送": "chuán sòng",
    "传达": "chuán dá", "遗传": "yí chuán", "流传": "liú chuán", "宣传": "xuān chuán",
    "传统": "chuán tǒng", "传承": "chuán chéng", "传感器": "chuán gǎn qì",
    "传记": "zhuàn jì", "自传": "zì zhuàn",
    # 分 words
    "分类": "fēn lèi", "分析": "fēn xī", "分布": "fēn bù", "分割": "fēn gē",
    "分开": "fēn kāi", "分离": "fēn lí", "分裂": "fēn liè", "分配": "fēn pèi",
    "分享": "fēn xiǎng", "分支": "fēn zhī", "分段": "fēn duàn", "分词": "fēn cí",
    "分页": "fēn yè", "分钟": "fēn zhōng", "区分": "qū fēn", "划分": "huà fēn",
    "拆分": "chāi fēn",
    "部分": "bù fèn", "成分": "chéng fèn", "充分": "chōng fèn", "分量": "fèn liàng",
    # 量 words
    "数量": "shù liàng", "质量": "zhì liàng", "流量": "liú liàng", "容量": "róng liàng",
    "能量": "néng liàng", "变量": "biàn liàng", "常量": "cháng liàng", "向量": "xiàng liàng",
    "增量": "zēng liàng", "存量": "cún liàng", "总量": "zǒng liàng", "批量": "pī liàng",
    "海量": "hǎi liàng", "大量": "dà liàng", "少量": "shǎo liàng",
    "测量": "cè liáng",
    # 度 words
    "速度": "sù dù", "精度": "jīng dù", "程度": "chéng dù", "角度": "jiǎo dù",
    "维度": "wéi dù", "深度": "shēn dù", "高度": "gāo dù", "长度": "cháng dù",
    "宽度": "kuān dù", "温度": "wēn dù", "湿度": "shī dù", "亮度": "liàng dù",
    "灵敏度": "líng mǐn dù",
    # 模 words
    "模型": "mó xíng", "模式": "mó shì", "模块": "mó kuài", "模拟": "mó nǐ",
    "模仿": "mó fǎng", "规模": "guī mó", "模糊": "mó hú", "模范": "mó fàn",
    "模组": "mó zǔ", "大模型": "dà mó xíng", "小模型": "xiǎo mó xíng", "语言模型": "yǔ yán mó xíng",
    "模样": "mú yàng", "模子": "mú zi", "模具": "mú jù", "模板": "mú bǎn",
    # 乐 words
    "音乐": "yīn yuè", "乐曲": "yuè qǔ", "乐器": "yuè qì", "乐谱": "yuè pǔ",
    "乐队": "yuè duì", "乐团": "yuè tuán", "声乐": "shēng yuè",
    "快乐": "kuài lè", "乐趣": "lè qù", "乐观": "lè guān", "欢乐": "huān lè",
    # 了 words
    "了解": "liǎo jiě", "了然": "liǎo rán",
    # 为 words
    "为了": "wèi le", "因为": "yīn wèi", "为什么": "wèi shén me",
    "作为": "zuò wéi", "成为": "chéng wéi", "认为": "rèn wéi", "以为": "yǐ wéi",
    "行为": "xíng wéi", "人为": "rén wéi",
    # 处 words
    "处理": "chǔ lǐ", "处置": "chǔ zhì", "处于": "chǔ yú", "相处": "xiāng chǔ",
    "用处": "yòng chù", "好处": "hǎo chù", "到处": "dào chù", "深处": "shēn chù",
    # 发 words
    "发送": "fā sòng", "发布": "fā bù", "发展": "fā zhǎn", "发现": "fā xiàn",
    "发生": "fā shēng", "发起": "fā qǐ", "发表": "fā biǎo", "发明": "fā míng",
    "开发": "kāi fā", "研发": "yán fā", "触发": "chù fā", "激发": "jī fā",
    "并发": "bìng fā",
    "头发": "tóu fà", "理发": "lǐ fà", "发型": "fà xíng",
    # 称 words
    "名称": "míng chēng", "称为": "chēng wéi", "称作": "chēng zuò", "简称": "jiǎn chēng",
    "对称": "duì chèn", "匀称": "yún chèn",
    # 识 words
    "认识": "rèn shí", "知识": "zhī shí", "意识": "yì shí", "识别": "shí bié",
    "共识": "gòng shí", "常识": "cháng shí",
    "标识": "biāo zhì",
    # 空 words
    "空间": "kōng jiān", "天空": "tiān kōng", "空气": "kōng qì", "航空": "háng kōng",
    "太空": "tài kōng", "真空": "zhēn kōng", "空调": "kōng tiáo",
    "空白": "kòng bái", "空格": "kòng gé", "空缺": "kòng quē", "空闲": "kòng xián",
    # 更 words
    "更新": "gēng xīn", "更改": "gēng gǎi", "更换": "gēng huàn", "更替": "gēng tì",
    "变更": "biàn gēng",
    "更加": "gèng jiā", "更好": "gèng hǎo", "更多": "gèng duō", "更快": "gèng kuài",
    "更高": "gèng gāo", "更强": "gèng qiáng", "更大": "gèng dà",
    # 相 words
    "相关": "xiāng guān", "相同": "xiāng tóng", "相似": "xiāng sì", "相比": "xiāng bǐ",
    "相对": "xiāng duì", "互相": "hù xiāng", "相信": "xiāng xìn", "相当": "xiāng dāng",
    "相机": "xiàng jī", "相片": "xiàng piàn", "照相": "zhào xiàng", "真相": "zhēn xiàng",
    # 系 words
    "系统": "xì tǒng", "系列": "xì liè", "关系": "guān xì", "联系": "lián xì",
    "体系": "tǐ xì", "操作系统": "cāo zuò xì tǒng", "文件系统": "wén jiàn xì tǒng",
    # 解 words
    "解决": "jiě jué", "解析": "jiě xī", "解释": "jiě shì", "解码": "jiě mǎ",
    "解压": "jiě yā", "解密": "jiě mì", "理解": "lǐ jiě", "分解": "fēn jiě",
    "讲解": "jiǎng jiě", "了解": "liǎo jiě", "化解": "huà jiě",
    # 率 words
    "比率": "bǐ lǜ", "概率": "gài lǜ", "频率": "pín lǜ", "速率": "sù lǜ",
    "利率": "lì lǜ", "汇率": "huì lǜ", "税率": "shuì lǜ", "功率": "gōng lǜ",
    "准确率": "zhǔn què lǜ", "命中率": "mìng zhòng lǜ", "成功率": "chéng gōng lǜ",
    "效率": "xiào lǜ", "率领": "shuài lǐng", "率先": "shuài xiān",
    # 间 words
    "时间": "shí jiān", "空间": "kōng jiān", "之间": "zhī jiān", "期间": "qī jiān",
    "中间": "zhōng jiān", "房间": "fáng jiān", "瞬间": "shùn jiān",
    "间隔": "jiàn gé", "间断": "jiàn duàn", "间接": "jiàn jiē",
    # 切 words
    "切割": "qiē gē", "切分": "qiē fēn", "切换": "qiē huàn", "切片": "qiē piàn",
    "切入": "qiē rù", "切断": "qiē duàn",
    "一切": "yī qiè", "切身": "qiè shēn", "切实": "qiè shí", "亲切": "qīn qiè",
    "密切": "mì qiè", "迫切": "pò qiè",
    # 便 words
    "方便": "fāng biàn", "便于": "biàn yú", "便利": "biàn lì", "便捷": "biàn jié",
    "顺便": "shùn biàn", "随便": "suí biàn", "即便": "jí biàn",
    "便宜": "pián yi",
    # 应 words
    "应该": "yīng gāi", "应当": "yīng dāng",
    "响应": "xiǎng yìng", "应用": "yìng yòng", "应答": "yìng dá", "适应": "shì yìng",
    "对应": "duì yìng", "反应": "fǎn yìng", "效应": "xiào yìng",
    # 还 words
    "还原": "huán yuán", "归还": "guī huán", "偿还": "cháng huán",
    "还是": "hái shì", "还有": "hái yǒu", "还要": "hái yào",
    # 强 words
    "强大": "qiáng dà", "强调": "qiáng diào", "加强": "jiā qiáng", "增强": "zēng qiáng",
    "强化": "qiáng huà", "强劲": "qiáng jìng", "强烈": "qiáng liè", "坚强": "jiān qiáng",
    "勉强": "miǎn qiǎng", "强迫": "qiǎng pò",
    # 背 words
    "背景": "bèi jǐng", "背后": "bèi hòu", "背面": "bèi miàn", "后背": "hòu bèi",
    "背包": "bēi bāo", "背负": "bēi fù",
    # 折 words
    "折扣": "zhé kòu", "折叠": "zhé dié", "折线": "zhé xiàn", "打折": "dǎ zhé",
    "曲折": "qū zhé", "挫折": "cuò zhé", "转折": "zhuǎn zhé",
    "折腾": "zhē teng",
}


def get_all_polyphone_words():
    """Get flattened dict of all words with their full pronunciation"""
    return WORD_PRONUNCIATIONS.copy()


def find_polyphone_chars(text):
    """Find all polyphone characters in text"""
    chars = set(POLYPHONE_DATABASE.keys())
    found = []
    for i, c in enumerate(text):
        if c in chars:
            found.append((i, c))
    return found


def suggest_pronunciation(char, context_before, context_after):
    """Suggest pronunciation based on surrounding context

    Returns:
        (full_word_pinyin, matched_word) - full pinyin for the word, and the word matched
        or (default_char_pinyin, None) if no word match found
    """
    if char not in POLYPHONE_DATABASE:
        return None, None

    data = POLYPHONE_DATABASE[char]
    context = context_before + char + context_after

    # First, try to match against known words (longest match first)
    sorted_words = sorted(WORD_PRONUNCIATIONS.keys(), key=len, reverse=True)
    for word in sorted_words:
        if char in word and word in context:
            return WORD_PRONUNCIATIONS[word], word

    # Fallback: check context patterns from database
    for pinyin, patterns in data["contexts"].items():
        for pattern in patterns:
            if pattern in context:
                # Try to get full word pronunciation
                if pattern in WORD_PRONUNCIATIONS:
                    return WORD_PRONUNCIATIONS[pattern], pattern
                # Return just the character pinyin with pattern info
                return pinyin, pattern

    return data["default"], None
