"""
Setup script for SOMARS Vision
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="somars-vision",
    version="0.1.0",
    author="Slugbotics",
    description="YOLO Object Detection for SUAS Competition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Slugbotics/somars-vision",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ultralytics>=8.0.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "PyYAML>=6.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
    ],
    entry_points={
        "console_scripts": [
            "somars-detect=src.detector:main",
        ],
    },
)
