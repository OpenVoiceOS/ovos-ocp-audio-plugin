#!/usr/bin/env python3
from setuptools import setup

# skill_id=package_name:SkillClass
PLUGIN_ENTRY_POINT = 'skill-playback-control.mycroftai=ovos_tskill_mycroft_cps:PlaybackControlSkill'

setup(
    # this is the package name that goes on pip
    name='ovos-tskill-mycroft-cps',
    version='0.0.1',
    description='this is a OVOS test skill for the mycroft common play framework',
    url='https://github.com/OpenVoiceOS/skill-abort-test',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    package_dir={"ovos_tskill_mycroft_cps": ""},
    package_data={'ovos_tskill_mycroft_cps': ['locale/*']},
    packages=['ovos_tskill_mycroft_cps'],
    include_package_data=True,
    install_requires=["ovos-workshop"],
    keywords='ovos skill plugin',
    entry_points={'ovos.plugin.skill': PLUGIN_ENTRY_POINT}
)
