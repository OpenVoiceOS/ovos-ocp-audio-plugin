#!/usr/bin/env python3
from setuptools import setup


PLUGIN_ENTRY_POINT = 'ovos_common_play=ovos_plugin_common_play'

setup(
    name='ovos_plugin_common_play',
    version='0.0.1a2',
    description='OVOS common play audio service adapter plugin',
    url='https://github.com/OpenVoiceOS/ovos-common-play-plugin',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['ovos_plugin_common_play'],
    install_requires=["ovos-plugin-manager>=0.0.1a3",
                      "audio-metadata",
                      "ovos_plugin_vlc>=0.0.1a3",
                      "padacioso",
                      "youtube-dl",
                      "ovos_workshop>=0.0.5a1"],
    zip_safe=True,
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
    entry_points={'mycroft.plugin.audioservice': PLUGIN_ENTRY_POINT}
)
