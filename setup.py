#!/usr/bin/env python3
import os
import re

from setuptools import setup


def get_version():
    fn = os.path.join(os.path.dirname(__file__), "formasaurus", "__init__.py")
    with open(fn) as f:
        return re.findall(r'__version__ = "([\d\.\w]+)"', f.read())[0]


with_deps_extras = [
    "joblib >= 1.2.0",
    "lxml >= 4.4.1",
    "lxml-html-clean >= 0.1.0",
    "scikit-learn >= 0.24.0",
    "scipy >= 1.5.1",
    "sklearn-crfsuite >= 0.5.0",
]

setup(
    name="formasaurus",
    version=get_version(),
    author="Mikhail Korobov",
    author_email="kmike84@gmail.com",
    license="MIT license",
    long_description=open("README.rst").read() + "\n\n" + open("CHANGES.rst").read(),
    description="Formasaurus tells you the types of HTML forms and their fields using machine learning",
    url="https://github.com/TeamHG-Memex/Formasaurus",
    zip_safe=False,
    packages=["formasaurus"],
    install_requires=[
        "docopt >= 0.4.0",
        "requests >= 1.0.0",
        "tldextract >= 1.2.0",
        "tqdm >= 2.0",
        "w3lib >= 1.13.0",
    ],
    package_data={
        "formasaurus": ["data/*.json", "data/html/*.html"],
    },
    extras_require={
        # Work around https://github.com/pypa/pip/issues/3032
        "with-deps": with_deps_extras,
        "with_deps": with_deps_extras,
        "annotation": [
            "ipython[notebook] >= 4.0",
            "ipywidgets",
            "Tornado>=4.0.0",
        ],
    },
    entry_points={"console_scripts": ["formasaurus = formasaurus.__main__:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
