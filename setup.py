from setuptools import setup, find_packages
setup(
    name = "husky",
    version = "0.1",
    packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    entry_points = {
        "console_scripts" : [
            'husky = husky.__main__:main'
        ]
    }
)