import shutil
from os import makedirs
from os.path import expanduser, isfile, join, dirname, exists
from ovos_config import Configuration
from ovos_utils.log import LOG
from ovos_plugin_manager.ocp import load_stream_extractors, available_extractors
from functools import wraps


def validate_message_context(message, native_sources=None):
    destination = message.context.get("destination")
    if destination:
        native_sources = native_sources or Configuration()["Audio"].get(
            "native_sources", ["debug_cli", "audio"]) or []
        if any(s in destination for s in native_sources):
            # request from device
            return True
        # external request, do not handle
        return False
    # broadcast for everyone
    return True


def require_native_source():

    def _decorator(func):
        @wraps(func)
        def func_wrapper(self, message=None):
            validated = message is None or \
                        not self.validate_source or \
                        validate_message_context(message, self.native_sources)
            if validated:
                return func(self, message)
            LOG.debug("ignoring OCP bus message, not from a native audio source")
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
