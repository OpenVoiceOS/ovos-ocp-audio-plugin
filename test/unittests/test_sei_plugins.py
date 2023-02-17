import unittest

from ovos_plugin_manager.ocp import StreamHandler


class TestOCPExtractor(unittest.TestCase):

    def test_news(self):
        parser = StreamHandler()
        news_urls = [
            "https://www.raiplaysound.it",
            "https://www.tsf.pt/stream",
            "https://www.abc.net.au/news",
            "https://www.ft.com",
            "https://www.npr.org/rss/podcast.php",
            "http://feeds.feedburner.com/gpbnews"
        ]
        for url in news_urls:
            print(f"#### {url}")
            meta = parser.extract_stream(url) or {}
            self.assertTrue(bool(meta.get("uri")))
            meta = parser.extract_stream(f"news//{url}") or {}
            self.assertTrue(bool(meta.get("uri")))


if __name__ == '__main__':
    unittest.main()
