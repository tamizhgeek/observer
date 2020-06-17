# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip

pfile = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pfile['packages'], r=False)
test_requirements = convert_deps_to_pip(pfile['dev-packages'], r=False)

setup(
    name='observer',
    version='0.0.1',
    description='Observer to monitor and record website uptimes and misc checks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tamizhgeek/observer',
    author='tamizhgeek',
    author_email='tamizhgeek@gmail.com',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Monitoring',
        'License :: OSI Approved :: Apache 2.0 License',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(where='.'),
    python_requires='>=3.5, <4',
    install_requires=requirements,
    extras_require={
        'test': test_requirements,
    },

    entry_points={
        'console_scripts': [
            'observer_source=source.run:run',
            'observer_sink=sink.run:run',
            'observer_fixtures=sink.db.fixtures:run'
        ],
    }
)
