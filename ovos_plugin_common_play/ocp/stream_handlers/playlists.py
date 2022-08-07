from ovos_ocp_m3u_plugin import OCPPlaylistExtractor


def get_playlist_stream(uri):
    extractor = OCPPlaylistExtractor()
    return extractor.extract_stream(uri)


