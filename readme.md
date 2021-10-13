# OCP - OVOS Common Play

![](./ovos_plugin_common_play/ocp/res/ui/images/ocp.png) 

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
      "vlc": {
        "type": "ovos_vlc",
        "active": true
      }
    },
    "default-backend": "local"
  }
}
```