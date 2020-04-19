# Webthing Home Assistant component

A full featured Homeassistant component to control Webthing. This component is based on my library available [here](https://github.com/hidaris/aiowebthing).

### Installation

Copy this folder to `<config_dir>/custom_components/webthing/`.

Add the following entry in your `configuration.yaml`:

```yaml
light:
  - platform: webthing
    host: HOST_HERE
```
