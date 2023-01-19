import mimetypes
import shutil
from os import makedirs
from os.path import expanduser, isfile, join, dirname

from ovos_plugin_manager.ocp import StreamHandler
from ovos_plugin_common_play.ocp.status import TrackState, PlaybackType
from ovos_ocp_files_plugin.plugin import OCPFilesMetadataExtractor
ocp_plugins = StreamHandler()


def find_mime(uri):
    """ Determine mime type. """
    mime = mimetypes.guess_type(uri)
    if mime:
        return mime
    else:
        return None


def available_extractors():
    return ["/", "http"] + \
           [f"{sei}//" for sei in ocp_plugins.supported_seis]


def extract_metadata(uri):
    # backwards compat
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
