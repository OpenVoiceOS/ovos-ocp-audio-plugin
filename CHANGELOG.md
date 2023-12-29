# Changelog

## [0.0.6a11](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/0.0.6a11) (2023-12-29)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a10...0.0.6a11)

**Merged pull requests:**

- Update requirements.txt [\#102](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/102) ([JarbasAl](https://github.com/JarbasAl))

## [V0.0.6a10](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a10) (2023-12-29)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a9...V0.0.6a10)

**Merged pull requests:**

- bump requirements [\#101](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/101) ([JarbasAl](https://github.com/JarbasAl))

## [V0.0.6a9](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a9) (2023-10-27)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a8...V0.0.6a9)

**Merged pull requests:**

- Update requirements to stable versions [\#100](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/100) ([NeonDaniel](https://github.com/NeonDaniel))

## [V0.0.6a8](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a8) (2023-09-12)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a7...V0.0.6a8)

**Implemented enhancements:**

- Add standalone launcher [\#97](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/97) ([Ramblurr](https://github.com/Ramblurr))

## [V0.0.6a7](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a7) (2023-08-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a6...V0.0.6a7)

**Merged pull requests:**

- OCPQuery: Only check if the gui is connected once [\#96](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/96) ([Ramblurr](https://github.com/Ramblurr))

## [V0.0.6a6](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a6) (2023-08-21)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a5...V0.0.6a6)

**Fixed bugs:**

- Allow `PlaybackType.SKILL` search results to be played when there is no GUI [\#95](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/95) ([Ramblurr](https://github.com/Ramblurr))

**Closed issues:**

- OCP search results are not processed fast enough because `is_gui_connected(..)` takes too long [\#93](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/issues/93)
- OCP skills supporting PlaybackType.SKILL cannot be played when there is no GUI [\#92](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/issues/92)

**Merged pull requests:**

- Handle race condition between `ovos.common_play.query.response` and `ovos.common_play.skill.search_end` [\#94](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/94) ([Ramblurr](https://github.com/Ramblurr))

## [V0.0.6a5](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a5) (2023-07-19)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a4...V0.0.6a5)

**Merged pull requests:**

- Update GUI to pass resource names instead of paths [\#90](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/90) ([NeonDaniel](https://github.com/NeonDaniel))

## [V0.0.6a4](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a4) (2023-07-13)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a3...V0.0.6a4)

**Fixed bugs:**

- fix/support for ui directories param [\#87](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/87) ([JarbasAl](https://github.com/JarbasAl))

## [V0.0.6a3](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a3) (2023-07-12)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a2...V0.0.6a3)

**Merged pull requests:**

- Update requirements.txt [\#86](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/86) ([JarbasAl](https://github.com/JarbasAl))

## [V0.0.6a2](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a2) (2023-06-14)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.6a1...V0.0.6a2)

**Closed issues:**

- All media play requests loop \(silently\) until ovos restart [\#84](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/issues/84)
- self.active\_backend is undefined when fallback is triggered [\#82](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/issues/82)

**Merged pull requests:**

- Refactor init to resolve deprecation warnings [\#85](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/85) ([NeonDaniel](https://github.com/NeonDaniel))

## [V0.0.6a1](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/tree/V0.0.6a1) (2023-04-23)

[Full Changelog](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/compare/V0.0.5...V0.0.6a1)

**Implemented enhancements:**

- Replace mycroft\_bus\_client with ovos\_bus\_client [\#80](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/80) ([goldyfruit](https://github.com/goldyfruit))

**Merged pull requests:**

- Fix automation typos [\#77](https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/pull/77) ([NeonDaniel](https://github.com/NeonDaniel))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
