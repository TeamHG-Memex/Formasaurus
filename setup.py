#!/usr/bin/env python
from setuptools import setup
import re
import os


def get_version():
    fn = os.path.join(os.path.dirname(__file__), "formasaurus", "__init__.py")
    with open(fn) as f:
        return re.findall("__version__ = '([\d\.\w]+)'", f.read())[0]


setup(
    name='formasaurus',
    version=get_version(),
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',
    license='MIT license',
    long_description=open('README.rst').read() + "\n\n" + open('CHANGES.rst').read(),
    description="HTML form type detector",
    url='https://github.com/TeamHG-Memex/Formasaurus',
    zip_safe=False,
    packages=['formasaurus'],
    install_requires=[
        "tqdm >= 2.0",
        "tldextract",
        "docopt",
        "six",
        "requests",
    ],
    package_data={
        'formasaurus': [
            'data/*.json',
            'data/html/*.html'
        ],
    },
    extras_require={
        'with-deps': [
            'scikit-learn >= 0.17',
            'scipy',
            'lxml',
            'sklearn-crfsuite >= 0.3.1',
        ],
        'annotation': [
            'ipython[notebook] >= 4.0',
            'ipywidgets',
        ],
    },
    entry_points={
        'console_scripts': ['formasaurus = formasaurus.__main__:main']
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
