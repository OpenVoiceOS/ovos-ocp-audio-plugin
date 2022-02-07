from ovos_plugin_common_play.ocp.search import OCPQuery, MediaType
from pprint import pprint
from ovos_utils.messagebus import get_mycroft_bus

bus = get_mycroft_bus()

search = OCPQuery("metallica")
search.bind(bus)
search.send()
search.wait()

for response in search.results:
    res = [r for r in response["results"]
           if r["match_confidence"] >= 25]
    if res:
        pprint(res)

search.close()

