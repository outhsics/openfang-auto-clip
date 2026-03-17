from setuptools import setup


setup(
    name="openfang-auto-clip",
    version="0.3.0",
    description="Local-first video repurposing pipeline with reproducible benchmark and clip export.",
    py_modules=["auto_clip", "web_manager"],
    packages=["src"],
    install_requires=[
        "Flask>=3.0.0",
        "requests>=2.31.0",
        "yt-dlp>=2024.1.1",
        "openai-whisper>=20231117",
    ],
    extras_require={"dev": ["pytest>=8.0.0"]},
    entry_points={"console_scripts": ["openfang-auto-clip=auto_clip:main"]},
)
