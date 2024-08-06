# OCP - OVOS Common Play

![](./ovos_plugin_common_play/ocp/res/desktop/OCP.png) 


OVOS Common Play is a full-fledged voice media player packaged as a mycroft audio plugin.

OCP handles the whole voice integration and playback functionality, it also integrates with external players via MPRIS

Skills provide search results, think about them as media providers/catalogs for OCP

You can find OCP skills in the [awesome-ocp-skills](https://github.com/OpenVoiceOS/awesome-ocp-skills) list 


## Configuration

mycroft.conf

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

Normally OCP is initialized and started by [ovos-audio](https://github.com/OpenVoiceOS/ovos-audio).

However, in some situations you may want to run OCP in standalone mode.

For example, when running Hivemind Core with Hivemind Satellites, you want to
run OCP at the Core, not the Satellite. You cannot run OCP on the satellite
because it cannot register its intents. So you want to run OCP in standalone
mode near to the Core.

How you do this depends on your setup. This packages provides the console script
`ovos-ocp-standalone`. So running in standalone mode could be as simple as:

``` shell
pip install ovos-plugin-common-play
ovos-ocp-standalone
```

It will read the configuration from `~/.config/mycroft/mycroft.conf` just like
all other OVOS applications.
