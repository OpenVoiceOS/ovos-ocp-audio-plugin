import re
import shutil
from functools import wraps
from os import makedirs
from os.path import expanduser, isfile, join, dirname, exists
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from ovos_bus_client.session import SessionManager
from ovos_plugin_manager.ocp import load_stream_extractors
from ovos_utils.log import LOG

# query string / path parameter names commonly used to carry secrets
# (auth tokens, api keys, session ids, ...) that must never be logged verbatim
_SENSITIVE_PARAM_RE = re.compile(
    r"(token|api[-_]?key|apikey|auth|password|passwd|secret|jwt|session[-_]?id|"
    r"access[-_]?token|x-plex-token)",
    re.IGNORECASE,
)


def redact_uri(uri):
    """Return `uri` with any sensitive query-string values (auth tokens,
    api keys, passwords, session ids, ...) replaced by 'REDACTED'.

    Safe to call on non-URI strings or malformed URIs - on any parsing
    failure the original value is returned unmodified rather than raising.
    """
    if not uri or not isinstance(uri, str):
        return uri
    try:
        parts = urlsplit(uri)
        if not parts.query:
            return uri
        redacted_qs = [
            (k, "REDACTED" if _SENSITIVE_PARAM_RE.search(k) else v)
            for k, v in parse_qsl(parts.query, keep_blank_values=True)
        ]
        new_query = urlencode(redacted_qs)
        return urlunsplit((parts.scheme, parts.netloc, parts.path,
                            new_query, parts.fragment))
    except Exception:
        return uri


def require_default_session():
    def _decorator(func):
        @wraps(func)
        def func_wrapper(self, message=None):
            sess = SessionManager.get(message)
            validated = message is None or \
                        not self.validate_source or \
                        sess.session_id == "default"
            if validated:
                return func(self, message)
            LOG.debug(f"ignoring OCP bus message, not from 'default' session': {message.context if message else sess.session_id}")
            return None

        return func_wrapper

    return _decorator


def ocp_plugins():
    return load_stream_extractors()


def is_qtav_available():
    return exists("/usr/include/qt/QtAV") or \
        exists("/usr/lib/qt/qml/QtAV") or \
        exists("/usr/lib/libQtAV.so")


def extract_metadata(uri):
    # backwards compat
    from ovos_ocp_files_plugin.plugin import OCPFilesMetadataExtractor
    return OCPFilesMetadataExtractor.extract_metadata(uri)


def create_desktop_file():
    res = join(dirname(__file__), "res", "desktop")
    desktop_path = expanduser("~/.local/share/applications")
    icon_path = expanduser("~/.local/share/icons")
    makedirs(desktop_path, exist_ok=True)
    makedirs(icon_path, exist_ok=True)

    src_desktop = join(res, "OCP.desktop")
    dst_desktop = join(desktop_path, "OCP.desktop")
    if not isfile(dst_desktop):
        shutil.copy(src_desktop, dst_desktop)

    src_icon = join(res, "OCP.png")
    dst_icon = join(icon_path, "OCP.png")
    if not isfile(dst_icon):
        shutil.copy(src_icon, dst_icon)
