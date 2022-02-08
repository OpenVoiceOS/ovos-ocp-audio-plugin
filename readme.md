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