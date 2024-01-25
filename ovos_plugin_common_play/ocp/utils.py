import shutil
from os import makedirs
from os.path import expanduser, isfile, join, dirname, exists
from typing import List

from ovos_ocp_files_plugin.plugin import OCPFilesMetadataExtractor
from ovos_plugin_manager.ocp import load_stream_extractors, available_extractors


def ocp_plugins():
    return load_stream_extractors()


def is_qtav_available():
    return exists("/usr/include/qt/QtAV") or \
        exists("/usr/lib/qt/qml/QtAV") or \
        exists("/usr/lib/libQtAV.so")


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
