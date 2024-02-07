import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setuptools.setup(
    name="warsaw_bus",
    version="0.0.1",
    author="Jan Opalski",
    author_email="jo448415@students.mimuw.edu.pl",
    description="University project about tracking Warsaw public transport",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mnemosyne1/warsaw_bus",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'pandas',
        'geopandas',
        'datetime',
        'plotly',
        'matplotlib',
        'geopy',
        'requests'
    ]
)
