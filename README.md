# OCP - OVOS Common Play

![](./ovos_plugin_common_play/ocp/res/desktop/OCP.png)

OVOS Common Play (OCP) is a voice media player packaged as a mycroft audio plugin. OCP handles voice integration and playback, and it also integrates with external players through MPRIS.

Skills provide the search results for OCP. Think of each skill as a media provider or catalog. You can find OCP skills in the [awesome-ocp-skills](https://github.com/OpenVoiceOS/awesome-ocp-skills) list.

## Configuration

Add this to `mycroft.conf`:

```json
{
  "Audio": {
    "backends": {
      "local": {
        "type": "ovos_common_play",
        "active": true
      },
      "simple": {
        "type": "ovos_audio_simple",
        "active": true
      }
    },
    "default-backend": "local"
  }
}
```

## Standalone Mode

> **DEPRECATED**: valid for ovos-core 0.0.7 only!

[ovos-audio](https://github.com/OpenVoiceOS/ovos-audio) normally starts and initializes OCP.

In some setups you may want to run OCP on its own. For example, if you run Hivemind Core with Hivemind Satellites, run OCP at the Core, not at a Satellite. A satellite cannot register OCP's intents, so run OCP in standalone mode near the Core instead.

The setup you use decides how you start standalone mode. This package provides the console script `ovos-ocp-standalone`, so running in standalone mode can be as simple as:

``` shell
pip install ovos-plugin-common-play
ovos-ocp-standalone
```

It reads its configuration from `~/.config/mycroft/mycroft.conf`, the same as other OVOS applications.
