from setuptools import setup, find_packages

setup(
    name="playwright-test-framework",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
    ],
)