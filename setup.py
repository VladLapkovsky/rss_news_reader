from setuptools import find_packages, setup

with open("requirements.txt") as file_to_read:
    REQUIRED = file_to_read.read().splitlines()

setup(
    py_modules=["__main__"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=REQUIRED,
    entry_points={"console_scripts": ["rss-reader=rss_parser.rss_reader:main"]},
)
