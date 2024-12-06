from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [
        line.strip() 
        for line in f.readlines() 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="knowledge-graph-poc",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.11",  # Based on your Python version
    entry_points={
        'console_scripts': [
            'kgraph=src.main:main',  # This allows us to run 'kgraph' from anywhere
        ],
    }
) 