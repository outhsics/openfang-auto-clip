#!/bin/bash
# Quick Start Script for Level 2 Testing
# Level 2 测试快速开始脚本

set -e

echo "🎬 OpenFang Auto Clip - Level 2 Testing Quick Start"
echo "🎬 OpenFang Auto Clip - Level 2 测试快速开始"
echo ""
echo "This script will help you start testing Level 2 script generation."
echo "此脚本将帮助您开始测试 Level 2 脚本生成。"
echo ""

# Check if we're in the repo root
if [ ! -f "auto_clip.py" ]; then
    echo "❌ Error: Please run this script from the repository root"
    echo "❌ 错误：请从仓库根目录运行此脚本"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p examples/level2_samples
mkdir -p ~/.openfang/clips/test_reports

# Check if demo transcript exists
DEMO_TRANSCRIPT="examples/demo/sample_level2_transcript.srt"
if [ ! -f "$DEMO_TRANSCRIPT" ]; then
    echo "❌ Error: Demo transcript not found: $DEMO_TRANSCRIPT"
    exit 1
fi

echo "✅ Demo transcript found"
echo ""

# Run Level 2 demo
echo "🧪 Running Level 2 demo test..."
echo "🧪 运行 Level 2 演示测试..."
echo ""

python3 auto_clip.py --demo-script-package

echo ""
echo "✅ Level 2 demo completed!"
echo "✅ Level 2 演示完成！"
echo ""

# Show output location
LATEST_PACKAGE=$(ls -td ~/.openfang/clips/script_packages/*/ 2>/dev/null | head -1)
if [ -n "$LATEST_PACKAGE" ]; then
    echo "📦 Package location: $LATEST_PACKAGE"
    echo "📦 脚本包位置: $LATEST_PACKAGE"
    echo ""
    echo "📝 Files generated:"
    echo "📝 生成的文件："
    echo "   • script_package.json"
    echo "   • script_draft.md"
    echo "   • production_blueprint.json"
    echo "   • operator_handoff.json"
    echo "   • review_report.json"
    echo "   • review_report.md"
    echo ""
fi

echo "🎯 Next Steps:"
echo "🎯 下一步："
echo ""
echo "1. Review the generated script package"
echo "1. 查看生成的脚本包"
echo "   cat \"$LATEST_PACKAGE/script_draft.md\""
echo ""
echo "2. Run the automated test script"
echo "2. 运行自动化测试脚本"
echo "   python3 scripts/test_level2_samples.py --all"
echo ""
echo "3. Add your own transcript samples to:"
echo "3. 将您自己的转录样本添加到："
echo "   examples/level2_samples/"
echo ""
echo "4. Fill out quality reports for each sample"
echo "4. 为每个样本填写质量报告"
echo "   cp examples/level2_samples/quality_report_template.md \\"
echo "      examples/level2_samples/quality_report_<sample_name>.md"
echo ""
echo "📚 Documentation:"
echo "📚 文档："
echo "   • examples/level2_samples/README.md - Sample collection guide"
echo "   • ROADMAP_v0.4.0.md - Development plan"
echo "   • DEVELOPMENT_PLAN_SUMMARY.md - Project summary"
echo ""

echo "✅ Setup complete! You're ready to test Level 2."
echo "✅ 设置完成！您已准备好测试 Level 2。"
