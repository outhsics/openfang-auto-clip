# Level 2 Test Samples / Level 2 测试样本

This directory contains diverse transcript samples for testing Level 2 script generation quality.

这个目录包含用于测试 Level 2 脚本生成质量的多样化转录样本。

---

## 📁 Sample Categories / 样本分类

### 1. Educational Content / 教育内容 (2 samples)
- `edu_tutorial_编程入门.srt` - Programming tutorial
- `edu_science_科学原理.srt` - Science concept explanation

### 2. Entertainment / 娱乐内容 (2 samples)
- `ent_comedy_喜剧片段.srt` - Comedy skit
- `ent_storytelling_故事讲述.srt` - Storytelling

### 3. Tutorial / How-To / 教程 (2 samples)
- `tut_cooking_烹饪教程.srt` - Cooking tutorial
- `tut_diy_手工制作.srt` - DIY craft tutorial

### 4. Multi-Language / 多语言 (4 samples)
- `lang_en_tech_英文科技.srt` - English tech review
- `lang_zh_business_中文商业.srt` - Chinese business talk
- `lang_en_edu_英文教育.srt` - English educational
- `lang_zh_lifestyle_中文生活.srt` - Chinese lifestyle

### 5. Different Lengths / 不同长度
- Short: 5-10 minutes
- Medium: 10-30 minutes
- Long: 30-60 minutes

---

## 📊 Quality Rubric / 质量评分标准

Each sample will be evaluated on:
每个样本将从以下维度评估：

### Script Quality / 脚本质量 (1-10)
- [ ] Coherence / 连贯性 - 脚本逻辑流畅
- [ ] Engagement / 吸引力 - 开头有吸引力
- [ ] Clarity / 清晰度 - 表达清晰明确
- [ ] Structure / 结构性 - 有清晰的开头、中间、结尾

### Actionability / 可操作性 (1-10)
- [ ] Visual Direction / 视觉指导 - 镜头指导具体
- [ ] Timing / 时序 - 时间分配合理
- [ ] Feasibility / 可行性 - 可以实际制作
- [ ] Asset Requests / 资产需求 - 素材需求明确

### Originality / 原创性 (1-10)
- [ ] Novel Phrasing / 新颖表达 - 避免直接复制
- [ ] Creative Angle / 创意角度 - 有新视角
- [ ] Value Retention / 价值保留 - 保留核心价值
- [ ] Copyright Safety / 版权安全 - 无版权风险

### Overall / 整体满意度 (1-10)
- [ ] Would Use / 愿意使用 - 愿意使用这个脚本
- [ ] Professional Quality / 专业质量 - 达到专业水平
- [ ] Platform Ready / 平台就绪 - 可直接发布

---

## 🧪 Testing Process / 测试流程

### Step 1: Run Level 2 / 运行 Level 2
```bash
python3 auto_clip.py --demo-script-package --transcript examples/level2_samples/<filename>
```

### Step 2: Review Output / 审查输出
- Check `~/.openfang/clips/script_packages/<timestamp>/`
- Review `script_draft.md`
- Check `review_report.md`

### Step 3: Score Quality / 评分
- Fill out the rubric in `quality_report_<sample>.md`
- Record specific issues
- Note improvements needed

### Step 4: Aggregate Results / 汇总结果
- Update `LEVEL2_QUALITY_REPORT.md`
- Calculate average scores
- Identify common issues

---

## 📝 Sample Template / 样本模板

When adding new samples, use this format:
添加新样本时使用此格式：

```srt
1
00:00:00,000 --> 00:00:05,000
[First 5 seconds of content]

2
00:00:05,000 --> 00:00:10,000
[Next 5 seconds]
...
```

---

## 🎯 Target Metrics / 目标指标

### Minimum Acceptable / 最低可接受
- Script Quality: 6/10
- Actionability: 6/10
- Originality: 7/10
- Overall: 6/10

### Production Ready / 生产就绪
- Script Quality: 8/10
- Actionability: 8/10
- Originality: 9/10
- Overall: 8/10

---

## 📊 Progress Tracking / 进度跟踪

| Sample | Type | Length | Status | Score | Notes |
|--------|------|--------|--------|-------|-------|
| demo_sample | Demo | 18s | ✅ Tested | TBD | Baseline |
| edu_tutorial_编程入门 | Edu | TBD | 📝 Planned | - | To add |
| edu_science_科学原理 | Edu | TBD | 📝 Planned | - | To add |
| ent_comedy_喜剧片段 | Ent | TBD | 📝 Planned | - | To add |
| ent_storytelling_故事讲述 | Ent | TBD | 📝 Planned | - | To add |
| tut_cooking_烹饪教程 | Tut | TBD | 📝 Planned | - | To add |
| tut_diy_手工制作 | Tut | TBD | 📝 Planned | - | To add |
| lang_en_tech_英文科技 | EN | TBD | 📝 Planned | - | To add |
| lang_zh_business_中文商业 | ZH | TBD | 📝 Planned | - | To add |

---

**Last Updated:** 2026-03-28
**Status:** 🚧 Setting up
**Next Action:** Collect real transcript samples
