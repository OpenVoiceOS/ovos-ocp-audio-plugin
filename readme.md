
# OCP - OVOS Common Play

in mycroft.conf

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