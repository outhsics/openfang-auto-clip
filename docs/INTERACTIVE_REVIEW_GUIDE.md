# Interactive Review Tool - User Guide

**Version:** 1.0
**Date:** 2026-03-29
**Status:** ✅ Ready to Use

---

## 🚀 Quick Start

### Installation

No additional installation needed. The tool is part of the main repository.

```bash
cd openfang-auto-clip
```

### Basic Usage

```bash
# Review the most recent package
python3 scripts/interactive_review.py --latest

# Review a specific package
python3 scripts/interactive_review.py --package ~/.openfang/clips/script_packages/TIMESTAMP_Title

# Review from package directory
python3 scripts/interactive_review.py --package ~/.openfang/clips/script_packages/TIMESTAMP_Title/script_package.json
```

---

## 📋 Menu Options

### 1. Overview
Display package statistics and section list.

**Shows:**
- Total sections
- Total duration
- Section names and durations
- Modification status

### 2. Sections
Review all sections one by one.

**Navigation:**
- Press Enter to continue to next section
- Type 's' to skip to next section
- Type 'q' to return to main menu

**Displays:**
- Section name and duration
- Narration text
- On-screen text
- Visual direction
- Source anchor (if available)

### 3. Quality
Show quality scores for the package.

**Scores:**
- Coherence (0-10)
- Actionability (0-10)
- Originality (0-10)
- Value Retention (0-10)
- Overall score with letter grade

**Suggestions:**
- Improvement recommendations for scores below 8/10

### 4. Edit
Edit a specific section.

**Editable Fields:**
1. **Narration**
   - Main script text
   - Similarity check after editing
   - Leave blank to keep current

2. **On-Screen Text**
   - Text overlay for video
   - Keep short (under 18 characters)

3. **Visual Direction**
   - Multi-line input supported
   - End with empty line to finish
   - Detailed shot specifications

**Process:**
1. Select section number
2. Edit desired fields
3. Leave blank to keep current value
4. Automatic similarity check for narration

### 5. Validate
Run comprehensive validation checks.

**Checks:**
- Copyright risk assessment
- Key point retention
- Similarity analysis
- Risk factor identification

**Results:**
- Risk level (minimal/low/medium/high)
- Risk score
- Safe for commercial use indicator
- Specific risk factors

### 6. Export
Export package to different formats.

**Formats:**
1. **Markdown (.md)** - Best for documentation
2. **JSON (.json)** - Pretty-printed, for programmatic use
3. **Text (.txt)** - Plain text, simple format

**Output:**
- Files saved in package directory
- Timestamped filenames
- Overwrites previous exports

### 7. Compare
Compare package with original transcript.

**Shows:**
- Original transcript excerpt
- Generated script sections
- Similarity scores per section
- Side-by-side comparison

### 8. Save
Save changes to package.

**Safety Features:**
- Automatic backup created
- Backup saved as `script_package.backup.json`
- Original timestamp preserved
- Modification flag cleared

### 9. Help
Show detailed help information.

**Topics:**
- Navigation tips
- Editing instructions
- Validation details
- Export options
- Safety features

### 0. Quit
Exit the review session.

**Behavior:**
- Prompts to save if changes exist
- Clean exit
- Goodbye message

---

## 💡 Tips & Best Practices

### Review Workflow

1. **Start with Overview** (Option 1)
   - Get familiar with package structure
   - Check section count and duration

2. **Check Quality Scores** (Option 3)
   - Identify areas needing improvement
   - Note low-scoring dimensions

3. **Review Sections** (Option 2)
   - Go through each section
   - Take notes on issues

4. **Edit Problem Areas** (Option 4)
   - Fix low-quality sections
   - Improve similarity issues
   - Enhance visual direction

5. **Validate Changes** (Option 5)
   - Run copyright risk check
   - Verify key point retention
   - Ensure quality improved

6. **Export for Production** (Option 6)
   - Export to preferred format
   - Use in video production

7. **Save Your Work** (Option 8)
   - Create backup automatically
   - Save changes

### Editing Guidelines

**Narration:**
- Keep conversational and engaging
- Avoid copying original text directly
- Target 60-80% similarity or lower
- Use content-type appropriate tone

**On-Screen Text:**
- Keep under 18 characters
- Use clear, concise language
- Match narration theme
- Consider platform (TikTok, Shorts, Reels)

**Visual Direction:**
- Be specific about shot types
- Include camera movements
- Specify framing and angles
- Add timing for each shot

### Quality Targets

**Production Ready:**
- Overall: 8.0+/10 (B+ or A)
- Coherence: 8.0+/10
- Actionability: 8.0+/10
- Originality: 9.0+/10
- Value Retention: 8.0+/10

**Acceptable:**
- Overall: 6.0+/10 (C or better)
- All dimensions: 6.0+/10

**Needs Improvement:**
- Overall: < 6.0/10
- Any dimension: < 6.0/10

### Copyright Safety

**Safe for Commercial Use:**
- Risk level: Minimal
- Risk score: < 0.2
- No direct quotations
- No phrase copying

**Requires Revision:**
- Risk level: Medium or High
- Risk score: ≥ 0.5
- Direct quotations present
- High similarity sections

---

## 🔧 Advanced Features

### Keyboard Shortcuts

**Main Menu:**
- `1` or `overview` - Show overview
- `2` or `sections` - Review sections
- `3` or `quality` - Show quality
- `4` or `edit` - Edit section
- `5` or `validate` - Run validation
- `6` or `export` - Export package
- `7` or `compare` - Compare with original
- `8` or `save` - Save changes
- `9` or `help` - Show help
- `0` or `q` or `quit` - Exit

**Section Review:**
- `Enter` - Continue to next section
- `s` - Skip to next section
- `q` - Return to main menu

### Multi-line Input

For visual direction editing, you can enter multi-line text:

```
Enter visual direction (multi-line, end with empty line): Shot 1: Close-up of face
Shot 2: Medium shot showing hands
Shot 3: Wide shot of environment
[Press Enter on empty line to finish]
```

### Automatic Backup

Every time you save changes:
1. Original file copied to `script_package.backup.json`
2. Changes written to `script_package.json`
3. Both files preserved in package directory

To restore from backup:
```bash
cp script_package.backup.json script_package.json
```

---

## 📊 Output Examples

### Quality Scores Output

```
🎯 QUALITY SCORES
=======================================================================

📊 Scores:
   ✅ Coherence: 10.0/10
   ✅ Actionability: 10.0/10
   🟡 Originality: 7.5/10
   ✅ Value Retention: 9.0/10

📈 Overall: 9.12/10 (A)
📌 Status: True

💡 Suggestions for improvement:
   • Rewrite to be more different from original
```

### Validation Output

```
⚖️  Copyright Risk Assessment:
   Risk Level: MEDIUM
   Risk Score: 0.55
   Safe for Commercial: ❌ No

   Risk Factors:
   • Direct_Quotation: 2 instances
   • Phrase_Copying: 5 instances

🔑 Key Point Retention:
   Retention Rate: 85.7%
   Status: ✅ Acceptable
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** "Package not found"
**Solution:** Ensure package path is correct. Use `--latest` for most recent package.

**Issue:** "Original transcript not available"
**Solution:** Comparison features require original transcript file. Ensure transcript exists.

**Issue:** "No sections to edit"
**Solution:** Package may be incomplete. Regenerate with complete Level 2 pipeline.

**Issue:** Changes not saving
**Solution:** Check file permissions. Ensure write access to package directory.

### Debug Mode

To see detailed error information:

```bash
python3 -u scripts/interactive_review.py --latest 2>&1 | tee debug.log
```

---

## 📚 Related Documentation

- `ROADMAP_v0.4.0.md` - Development roadmap
- `docs/LEVEL2_IMPROVEMENT_ANALYSIS.md` - Technical details
- `docs/PHASE1_WEEK2_COMPLETE.md` - Week 2 achievements
- `scripts/level2_validation.py` - Validation module documentation

---

## 🎓 Tutorial

### First-Time Review Session

```bash
# 1. Start the tool
python3 scripts/interactive_review.py --latest

# 2. View overview
# Choose: 1
# Review statistics and section list

# 3. Check quality
# Choose: 3
# Note which sections need improvement

# 4. Review sections
# Choose: 2
# Press Enter through each section
# Note issues and improvements needed

# 5. Edit first section
# Choose: 4
# Enter section number: 1
# Edit narration
# Leave other fields blank to keep current

# 6. Validate changes
# Choose: 5
# Check if similarity improved

# 7. Export for production
# Choose: 6
# Choose format: 1 (Markdown)

# 8. Save your work
# Choose: 8
# Verify backup created

# 9. Exit
# Choose: 0
# Confirm save if prompted
```

---

## 📞 Support

**Issues:** GitHub Issues - `bug` label
**Questions:** GitHub Discussions - `help` category
**Feature Requests:** GitHub Issues - `enhancement` label

---

**Last Updated:** 2026-03-29
**Tool Version:** 1.0
**Status:** ✅ Production Ready
