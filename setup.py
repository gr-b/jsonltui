from setuptools import setup, find_packages

setup(
    name='jsonltui',
    version='0.1.0',
    description="A TUI application to visually inspect and navigate JSON and JSONL data",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'textual',
    ],
    entry_points={
        'console_scripts': [
            'jsonltui=jsonltui.main:main',
        ],
    },
    package_data={
            'jsonltui': ['web_template.html'],
    },
    python_requires='>=3.7',
    license='MIT',
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/gr-b/jsonltui",
)