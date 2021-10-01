def get_bandcamp_audio_stream(url):
    from py_bandcamp import BandCamper
    data = BandCamper.get_stream_data(url)
    data["uri"] = data.pop("stream")
    return data


def is_bandcamp(url):
    if not url:
        return False
    return "bandcamp." in url
