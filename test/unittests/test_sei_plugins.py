import unittest

from ovos_plugin_manager.ocp import StreamHandler


class TestOCPExtractor(unittest.TestCase):

    def test_rss(self):
        parser = StreamHandler()
        rss_urls = [
            "https://www.spreaker.com/show/1401466/episodes/feed",
            "http://feeds.foxnewsradio.com/FoxNewsRadio",
            "https://www.pbs.org/newshour/feeds/rss/podcasts/show",
            "https://www.deutschlandfunk.de/podcast-nachrichten.1257.de.podcast.xml",
            "https://podcasts.files.bbci.co.uk/p02nq0gn.rss",
            "http://www.rtp.pt/play/podcast/7496",
            "https://www.cbc.ca/podcasting/includes/hourlynews.xml",
            "https://podcast.hr-online.de/der_tag_in_hessen/podcast.xml",
            "https://api.sr.se/api/rss/pod/3795",
            "http://api.rtve.es/api/programas/36019/audios.rs",
            "https://www.pbs.org/newshour/feeds/rss/podcasts/show",
            "https://feeds.yle.fi/areena/v1/series/1-1440981.rss",
            "https://de1.api.radio-browser.info/pls/url/69bc7084-523c-11ea-be63-52543be04c81"  # .pls
        ]
        for url in rss_urls:
            print(f"#### {url}")
            meta = parser.extract_stream(f"rss//{url}") or {}
            self.assertTrue(bool(meta.get("uri")))
            # test dropped news// sei
            meta = parser.extract_stream(f"news//rss//{url}") or {}
            self.assertTrue(bool(meta.get("uri")))

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
