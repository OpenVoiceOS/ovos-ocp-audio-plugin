#!/usr/bin/env python3
import os
from setuptools import setup, find_packages


BASEDIR = os.path.abspath(os.path.dirname(__file__))


def get_version():
    """ Find the version of the package"""
    version = None
    version_file = os.path.join(BASEDIR, 'ovos_plugin_common_play', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


def get_description():
    with open(os.path.join(BASEDIR, "README.md"), "r") as f:
        long_description = f.read()
    return long_description


PLUGIN_ENTRY_POINT = 'ovos_common_play=ovos_plugin_common_play'
PLUGIN_CONFIG_ENTRY_POINT = 'ovos_common_play.config=ovos_plugin_common_play:OCPPluginConfig'


setup(
    name='ovos_plugin_common_play',
    version=get_version(),
    description='OVOS common play audio service adapter plugin',
    long_description=get_description(),
    long_description_content_type="text/markdown",
    url='https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=find_packages(include=['ovos_plugin_common_play*']),
    install_requires=required("requirements/requirements.txt"),
    package_data={'': package_files('ovos_plugin_common_play')},
    extras_require={
        'extractors': required("requirements/requirements_extra.txt")
    },
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ovos audio plugin',
    entry_points = {
        "mycroft.plugin.audioservice": PLUGIN_ENTRY_POINT,
        "mycroft.plugin.audioservice.config": PLUGIN_CONFIG_ENTRY_POINT,
        "console_scripts": [
            "ovos-ocp-standalone=ovos_plugin_common_play.launcher:main"
        ],
    }
)
