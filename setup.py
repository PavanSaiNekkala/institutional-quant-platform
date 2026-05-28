from setuptools import (
    setup,
    find_packages
)

setup(

    name="institutional_quant",

    version="1.0.0",

    packages=find_packages(),

    install_requires=[

        "pandas",
        "numpy",
        "pyarrow",
        "fastparquet",
        "yfinance",
        "scikit-learn",
        "scipy",
        "streamlit",
        "plotly",
        "openpyxl"
    ],

    python_requires=">=3.11",
)