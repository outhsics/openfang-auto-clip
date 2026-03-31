"""
STT 提供商使用示例

演示如何使用不同的语音识别提供商
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enhancements.ai_providers import (
    get_stt_provider,
    auto_select_stt,
    GroqWhisperSTT,
    OpenAIWhisperSTT,
    LocalWhisperSTT,
    DeepgramSTT
)


def example_groq_whisper():
    """示例 1: 使用 Groq Whisper（超快速）"""
    print("\n🚀 示例 1: Groq Whisper - 超快速 STT")

    try:
        # 初始化 Groq Whisper
        stt = GroqWhisperSTT()

        # 转录音频
        audio_path = "path/to/your/audio.mp3"
        result = stt.transcribe(
            audio_path,
            language="auto"  # 自动检测语言
        )

        print(f"✅ 转录成功!")
        print(f"文本: {result.text}")
        print(f"语言: {result.language}")
        print(f"时长: {result.duration}秒")
        print(f"提供商: {result.provider}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请设置 GROQ_API_KEY 环境变量")


def example_openai_whisper():
    """示例 2: 使用 OpenAI Whisper（高质量）"""
    print("\n🎵 示例 2: OpenAI Whisper - 高质量 STT")

    try:
        # 初始化 OpenAI Whisper
        stt = OpenAIWhisperSTT()

        # 转录音频
        audio_path = "path/to/your/audio.mp3"
        result = stt.transcribe(
            audio_path,
            language="auto",
            model="whisper-1"  # 或 "whisper-large-v3"
        )

        print(f"✅ 转录成功!")
        print(f"文本: {result.text}")
        print(f"分段数: {len(result.segments)}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请设置 OPENAI_API_KEY 环境变量")


def example_local_whisper():
    """示例 3: 使用本地 Whisper（完全离线）"""
    print("\n🏠 示例 3: Local Whisper - 离线 STT")

    try:
        # 初始化本地 Whisper
        stt = LocalWhisperSTT(model_size="base")  # tiny, base, small, medium, large

        # 转录音频
        audio_path = "path/to/your/audio.mp3"
        result = stt.transcribe(
            audio_path,
            language="auto",
            fp16=False  # CPU 模式设为 False
        )

        print(f"✅ 转录成功!")
        print(f"文本: {result.text}")
        print(f"模型: {result.provider}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请安装 openai-whisper: pip install openai-whisper")


def example_deepgram():
    """示例 4: 使用 Deepgram（专业级）"""
    print("\n🎤 示例 4: Deepgram - 专业级 STT")

    try:
        # 初始化 Deepgram
        stt = DeepgramSTT()

        # 转录音频
        audio_path = "path/to/your/audio.mp3"
        result = stt.transcribe(
            audio_path,
            language="auto",
            model="nova-2"  # nova-2 是最快模型
        )

        print(f"✅ 转录成功!")
        print(f"文本: {result.text}")
        print(f"提供商: {result.provider}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请设置 DEEPGRAM_API_KEY 环境变量")


def example_auto_select():
    """示例 5: 自动选择最佳提供商"""
    print("\n🤖 示例 5: 自动选择 STT 提供商")

    try:
        # 自动选择可用的提供商
        stt = auto_select_stt()

        print(f"✅ 自动选择: {stt.__class__.__name__}")

        # 转录音频
        audio_path = "path/to/your/audio.mp3"
        result = stt.transcribe(audio_path)

        print(f"文本: {result.text}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        print("💡 提示: 请至少安装一个 STT 提供商")


def example_with_segments():
    """示例 6: 获取带时间戳的转录片段"""
    print("\n⏱️  示例 6: 获取带时间戳的转录片段")

    try:
        stt = get_stt_provider("groq_whisper")
        audio_path = "path/to/your/audio.mp3"

        result = stt.transcribe(audio_path)

        print(f"完整文本:\n{result.text}\n")
        print("时间片段:")

        for i, segment in enumerate(result.segments[:5], 1):
            start = segment['start']
            end = segment['end']
            text = segment['text']
            print(f"{i}. [{start:.2f}s - {end:.2f}s] {text}")

    except Exception as e:
        print(f"❌ 错误: {e}")


def compare_providers():
    """示例 7: 比较不同提供商"""
    print("\n📊 示例 7: 比较不同 STT 提供商")

    audio_path = "path/to/your/audio.mp3"

    providers = {
        "Groq Whisper": "groq_whisper",
        "OpenAI Whisper": "openai_whisper",
        "Local Whisper": "local_whisper"
    }

    results = {}

    for name, provider_id in providers.items():
        try:
            print(f"\n测试 {name}...")
            stt = get_stt_provider(provider_id)

            import time
            start_time = time.time()
            result = stt.transcribe(audio_path)
            elapsed = time.time() - start_time

            results[name] = {
                "text": result.text[:100] + "..." if len(result.text) > 100 else result.text,
                "time": elapsed,
                "language": result.language
            }

            print(f"✅ 成功! 耗时: {elapsed:.2f}秒")

        except Exception as e:
            print(f"❌ 失败: {e}")
            results[name] = {"error": str(e)}

    # 打印比较结果
    print("\n" + "="*60)
    print("比较结果:")
    print("="*60)

    for name, result in results.items():
        print(f"\n{name}:")
        if "error" in result:
            print(f"  ❌ {result['error']}")
        else:
            print(f"  ⏱️  耗时: {result['time']:.2f}秒")
            print(f"  🌍 语言: {result['language']}")
            print(f"  📝 文本: {result['text']}")


def main():
    """运行所有示例"""
    print("="*60)
    print("🎤 STT 提供商使用示例")
    print("="*60)

    # 运行单个示例
    # example_groq_whisper()
    # example_openai_whisper()
    # example_local_whisper()

    # 运行自动选择示例
    example_auto_select()

    # 比较提供商（需要有效的音频文件）
    # compare_providers()


if __name__ == "__main__":
    main()
