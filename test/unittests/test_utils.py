import unittest


class TestUtils(unittest.TestCase):

    def test_available_extractors(self):
        from ovos_plugin_manager.ocp import available_extractors
        extractors = available_extractors()
        self.assertIsInstance(extractors, list)
        for ex in extractors:
            self.assertIsInstance(ex, str)


class TestRedactURI(unittest.TestCase):
    """ regression tests for https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/issues/118
    auth tokens embedded in stream URIs (eg. Plex X-Plex-Token) must never be
    exposed verbatim in logs """

    def test_redacts_plex_token(self):
        from ovos_plugin_common_play.ocp.utils import redact_uri
        uri = ("https://192-168-86-60.4ed47cc43e8e4fb3b428b18a225184b0.plex.direct:32400"
               "/audio/:/transcode/universal/start.m3u8?path=%2Flibrary%2Fmetadata%2F9706"
               "&mediaIndex=0&partIndex=0&fastSeek=1&copyts=1&offset=0"
               "&X-Plex-Platform=Chrome&X-Plex-Token=SECRETVALUE")
        redacted = redact_uri(uri)
        self.assertNotIn("SECRETVALUE", redacted)
        # non-sensitive params must be preserved
        self.assertIn("mediaIndex=0", redacted)
        self.assertIn("X-Plex-Platform=Chrome", redacted)

    def test_redacts_generic_secret_params(self):
        from ovos_plugin_common_play.ocp.utils import redact_uri
        for param in ("token", "api_key", "apikey", "auth", "password",
                       "secret", "access_token", "session_id"):
            uri = f"https://example.com/stream?{param}=topsecret&foo=bar"
            redacted = redact_uri(uri)
            self.assertNotIn("topsecret", redacted,
                              f"param {param} was not redacted")
            self.assertIn("foo=bar", redacted)

    def test_uri_without_query_unchanged(self):
        from ovos_plugin_common_play.ocp.utils import redact_uri
        uri = "https://example.com/stream.mp3"
        self.assertEqual(redact_uri(uri), uri)

    def test_non_string_input_passthrough(self):
        from ovos_plugin_common_play.ocp.utils import redact_uri
        self.assertIsNone(redact_uri(None))
        self.assertEqual(redact_uri(""), "")

    def test_malformed_uri_does_not_raise(self):
        from ovos_plugin_common_play.ocp.utils import redact_uri
        # not a well formed URI, but redact_uri must never raise and must
        # still not leak an obvious token value
        weird = "not a uri ??? token=abc"
        redacted = redact_uri(weird)
        self.assertIsInstance(redacted, str)
        self.assertNotIn("abc", redacted)
