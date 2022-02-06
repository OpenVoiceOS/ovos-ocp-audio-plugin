import enum
import requests


class YoutubeBackend(str, enum.Enum):
    YDL = "youtube-dl"
    PYTUBE = "pytube"
    PAFY = "pafy"
    INVIDIOUS = "invidious"


class YdlBackend(str, enum.Enum):
    YDL = "youtube-dl"
    YDLC = "youtube-dlc"
    YDLP = "yt-dlp"


class YoutubeLiveBackend(str, enum.Enum):
    PYTUBE = "pytube"
    YT_SEARCHER = "youtube_searcher"


def _parse_title(title):
    # try to extract_streams artist from title
    delims = [":", "|", "-"]

    removes = ["(Official Video)", "(Official Music Video)",
               "(Lyrics)", "(Official)", "(Album Stream)",
               "(Legendado)"]
    removes += [s.replace("(", "").replace(")", "") for s in removes] + \
               [s.replace("[", "").replace("]", "") for s in removes]
    removes += [s.upper() for s in removes] + [s.lower() for s in removes]
    removes += ["(HQ)", "()", "[]", "- HQ -"]

    for d in delims:
        if d in title:
            for k in removes:
                title = title.replace(k, "")
            artist = title.split(d)[0]
            title = "".join(title.split(d)[1:])
            title = title.strip() or "..."
            artist = artist.strip() or "..."
            return title, artist
    return title.replace(" - Topic", ""), ""


def get_youtube_live_from_channel(url, backend=YoutubeLiveBackend.PYTUBE,
                                  fallback=True):
    if backend == YoutubeLiveBackend.PYTUBE:
        try:
            for vid in get_pytube_channel_livestreams(url):
                return vid
        except:
            if fallback:
                return get_youtube_live_from_channel(
                    url, backend=YoutubeLiveBackend.YT_SEARCHER, fallback=False)
            raise
    elif backend == YoutubeLiveBackend.YT_SEARCHER:
        try:
            for vid in get_youtubesearcher_channel_livestreams(url):
                return vid
        except:
            if fallback:
                return get_youtube_live_from_channel(
                    url, backend=YoutubeLiveBackend.PYTUBE,
                    fallback=False)
            raise
    else:
        if fallback:
            return get_youtube_live_from_channel(url,
                                                 backend=YoutubeLiveBackend.PYTUBE)
        raise ValueError("invalid backend")


def get_youtube_stream(url,
                       audio_only=False,
                       ocp_settings=None):
    settings = ocp_settings or {}
    backend = settings.get("youtube_backend") or YoutubeBackend.YDL
    if backend == YoutubeBackend.PYTUBE:
        extractor = get_pytube_stream
    elif backend == YoutubeBackend.PAFY:
        extractor = get_pafy_stream
    elif backend == YoutubeBackend.INVIDIOUS:
        extractor = get_invidious_stream
    else:
        extractor = get_ydl_stream
    return extractor(url, audio_only=audio_only, ocp_settings=settings)


def is_youtube(url):
    # TODO localization
    if not url:
        return False
    return "youtube.com/" in url or "youtu.be/" in url


def get_invidious_stream(url, audio_only=False, ocp_settings=None):
    # proxy via invidious instance
    # public instances: https://docs.invidious.io/Invidious-Instances.md
    # self host: https://github.com/iv-org/invidious

    settings = ocp_settings or {}
    host = settings.get("invidious_host") or "https://vid.puffyan.us"
    local = "true" if settings.get("proxy_invidious") else "false"

    vid_id = url.split("watch?v=")[-1].split("&")[0]
    stream = f"{host}/latest_version?id={vid_id}&itag=22&local={local}&subtitles=en"

    html = requests.get(f"{host}/watch?v={vid_id}").text

    info = {
        "uri": stream,
        "title": html.split("<title>")[-1].split("</title>")[0],
        "image": f"{host}/vi/{vid_id}/maxres.jpg",
        "length": float(html.split('"length_seconds":')[-1].split(",")[0]) * 1000
    }

    for m in html.split("<meta ")[1:]:
        if not m.startswith('name="'):
            continue

        if 'name="description"' in m:
            pass
        elif 'name="keywords"' in m:
            pass
        elif 'name="thumbnail"' in m:
            pic = m.split('content="')[-1].split(">")[0][:-1]
            info["image"] = f"{host}{pic}"

    return info


def get_ydl_stream(url, audio_only=False, ocp_settings=None,
                   preferred_ext=None, backend=YdlBackend.YDL,
                   fallback=True, ydl_opts=None, best=True):
    settings = ocp_settings or {}
    ydl_opts = ydl_opts or {
        "quiet": True,
        "hls_prefer_native": True,
        "verbose": False,
        "format": "best"
    }

    if backend == YdlBackend.YDLP:
        import yt_dlp as youtube_dl
    elif backend == YdlBackend.YDLC:
        import youtube_dlc as youtube_dl
    elif backend == YdlBackend.YDL:
        import youtube_dl
    else:
        raise ValueError("invalid youtube-dl backend")

    kmaps = {"duration": "duration",
             "thumbnail": "image",
             "uploader": "artist",
             "title": "title",
             'webpage_url': "url"}
    info = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        meta = ydl.extract_info(url, download=False)
        for k, v in kmaps.items():
            if k in meta:
                info[v] = meta[k]

        if "entries" in meta:
            meta = meta["entries"][0]

        info["uri"] = _select_ydl_format(meta, audio_only=audio_only,
                                         best=best)
        title, artist = _parse_title(info["title"])
        info["title"] = title
        info["artist"] = artist or info.get("artist")
        info["is_live"] = meta.get("is_live", False)
    return info


def _select_ydl_format(meta, audio_only=False, preferred_ext=None, best=True):
    if not meta.get("formats"):
        # not all extractors return same format dict
        if meta.get("url"):
            return meta["url"]
        raise ValueError

    fmts = meta["formats"]
    if audio_only:
        # skip any stream that contains video
        fmts = [f for f in fmts if f.get('vcodec', "") == "none"]
    else:
        # skip video only streams (no audio / progressive streams only)
        fmts = [f for f in fmts if f.get('acodec', "") != "none"]

    if preferred_ext:
        fmts = [f for f in meta["formats"]
                if f.get('ext', "") == preferred_ext] or fmts

    # last is best (higher res)
    if best:
        return fmts[-1]["url"]
    return fmts[0]["url"]


def get_pafy_stream(url,  audio_only=False, ocp_settings=None):
    import pafy
    settings = ocp_settings or {}
    stream = pafy.new(url)
    meta = {
        "url": url,
        # "audio_stream": stream.getbestaudio().url,
        # "stream": stream.getbest().url,
        "author": stream.author,
        "image": stream.getbestthumb().split("?")[0],
        #        "description": stream.description,
        "length": stream.length * 1000,
        "category": stream.category,
        #        "upload_date": stream.published,
        #        "tags": stream.keywords
    }

    # TODO fastest vs best
    stream = None
    if audio_only:
        stream = stream.getbestaudio() or stream.getbest()
    else:
        stream = stream.getbest()
    if not stream:
        raise RuntimeError("Failed to extract stream")
    uri = stream.url
    meta["uri"] = uri
    title, artist = _parse_title(stream.title)
    meta["title"] = title
    meta["artist"] = artist or stream.author
    return meta


def get_pytube_stream(url, audio_only=False, ocp_settings=None, best=True):
    from pytube import YouTube
    settings = ocp_settings or {}
    yt = YouTube(url)
    s = None
    if audio_only:
        s = yt.streams.filter(only_audio=True).order_by('abr')
    if not s:
        s = yt.streams.filter(progressive=True).order_by('resolution')

    if best:  # best quality
        s = s.last()
    else:  # fastest
        s = s.first()

    info = {
        "uri": s.url,
        "url": yt.watch_url,
        "title": yt.title,
        "author": yt.author,
        "image": yt.thumbnail_url,
        "length": yt.length * 1000
    }
    title, artist = _parse_title(info["title"])
    info["title"] = title
    info["artist"] = artist or info.get("author")
    return info


def get_pytube_channel_livestreams(url):
    from pytube import Channel
    yt = Channel(url)
    for v in yt.videos_generator():
        if v.vid_info.get('playabilityStatus', {}).get('liveStreamability'):
            title, artist = _parse_title(v.title)
            yield {
                "url": v.watch_url,
                "title": title,
                "artist": artist,
                "is_live": True,
                "image": v.thumbnail_url,
                "length": v.length * 1000
            }


def get_youtubesearcher_channel_livestreams(url):
    try:
        from youtube_searcher import extract_videos
        for e in extract_videos(url):
            if not e["is_live"]:
                continue
            title, artist = _parse_title(e["title"])
            yield {
                "url": "https://www.youtube.com/watch?v=" + e["videoId"],
                "is_live": True,
                "description": e["description"],
                "image": e["thumbnail"],
                "title": title,
                "artist": artist
            }
    except:
        pass
