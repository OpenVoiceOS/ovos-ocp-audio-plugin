from ovos_ocp_rss_plugin import OCPRSSFeedExtractor


def get_rss_first_stream(feed_url):
    extractor = OCPRSSFeedExtractor()
    return extractor.extract_stream(feed_url)
