import setuptools

# 读取README内容作为long_description
try:
    with open("../README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "MSIMG CLI - 魔塔社区文生图API命令行工具"

# 读取requirements
install_requires = [
    "click>=8.0.0",
    "requests>=2.31.0",
    "Pillow>=10.0.0",
    "msimg>=0.0.4"
]

# 可选依赖
extras_require = {
    "qiniu": ["qiniu>=7.12.0"],
    "aliyun": ["oss2>=2.18.0"],
    "upyun": ["upyun>=2.5.0"],
    "all": ["qiniu>=7.12.0", "oss2>=2.18.0", "upyun>=2.5.0"]
}

setuptools.setup(
    name="cli-anything-msimg",
    version="0.0.1",
    author="Xiaoqiang",
    author_email="xiaoqiangclub@hotmail.com",
    description="MSIMG CLI - 魔塔社区文生图API命令行工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiaoqiangclub/msimg",
    packages=setuptools.find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.8',
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'cli-anything-msimg=cli_anything.msimg.core.msimg_cli:cli',
        ],
    },
)