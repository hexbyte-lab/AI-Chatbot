from setuptools import setup, find_packages

setup(
    name="ai-chatbot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI Chatbot with conversation memory and streaming",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AI-Chatbot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "transformers>=4.35.0",
        "torch>=2.0.0",
        "accelerate>=0.25.0",
        "bitsandbytes>=0.41.0",
        "pyyaml>=6.0",
    ],
)
