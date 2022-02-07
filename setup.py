#!/usr/bin/env python3
from setuptools import setup


PLUGIN_ENTRY_POINT = 'ovos_common_play=ovos_plugin_common_play'

setup(
    name='ovos_plugin_common_play',
    version='0.0.1a10',
    description='OVOS common play audio service adapter plugin',
    url='https://github.com/OpenVoiceOS/ovos-common-play-plugin',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['ovos_plugin_common_play',
              'ovos_plugin_common_play.ocp',
              'ovos_plugin_common_play.ocp.stream_handlers'],
    install_requires=["ovos-plugin-manager>=0.0.1a3",
                      "ovos_audio_plugin_simple~=0.0.1a1",
                      "padacioso~=0.1.1",
                      "yt-dlp",
                      "dbus_next",
                      "ovos_workshop~=0.0.5a8"],
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
    entry_points={'mycroft.plugin.audioservice': PLUGIN_ENTRY_POINT}
)
