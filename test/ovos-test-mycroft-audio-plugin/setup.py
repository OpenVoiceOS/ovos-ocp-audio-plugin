#!/usr/bin/env python3
import os
from setuptools import setup

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


PLUGIN_ENTRY_POINT = 'ovos_test_mycroft_audio_plugin=ovos_test_mycroft_audio_plugin'

setup(
    name='ovos-test-mycroft-audio-plugin',
    version="0.0.1",
    description='test audio plugin for ovos-core',
    url='https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['ovos_test_mycroft_audio_plugin'],
    package_data={'': package_files('ovos_test_mycroft_audio_plugin')},
    keywords='ovos audio plugin',
    entry_points={'mycroft.plugin.audioservice': PLUGIN_ENTRY_POINT}
)
