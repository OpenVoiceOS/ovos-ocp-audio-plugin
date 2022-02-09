from ovos_plugin_common_play.ocp.search import OCPQuery, MediaType
from pprint import pprint


with OCPQuery("metallica") as search:
    search.send()
    search.wait()

    for response in search.results:
        res = [r for r in response["results"]
               if r["match_confidence"] >= 25]
        if res:
            pprint(res)

