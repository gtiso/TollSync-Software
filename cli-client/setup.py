from setuptools import setup

setup(
    name="se2451",
    version="1.0",
    py_modules=["cli_tool"],
    install_requires=["click", "requests"],
    entry_points={
        "console_scripts": [
            "se2451 = cli_tool:cli"
        ]
    },
)


# Step 1 : pip install --editable .
# Step 2 : se2451