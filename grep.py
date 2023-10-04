import datetime as dt
import json
import os
from urllib.request import urlopen

import lxml.html

URLS = {
    "2023": "https://www.praha5.cz/povinne-zverejnovane-informace/archiv-poskytnutych-informaci-podle-zakona-c-106-1999-sb/2023-2/",
}

tdir = "data"
os.makedirs(tdir, exist_ok=True)

for year, url in URLS.items():
    tfile = os.path.join(tdir, year + ".json")
    ht = lxml.html.parse(urlopen(url)).getroot()
    cmps = []
    for tr in ht.find(".//table").find("./tbody").findall(".//tr"):
        raw_date, raw_body = tr.getchildren()
        d, m, y = raw_date.text_content().split(".")

        cdate = dt.date(int(y), int(m), int(d)).isoformat()
        ccomp = raw_body.text_content().replace("\xa0", " ")
        curl = raw_body.find("a").attrib["href"]
        cmps.append(
            {
                "datum": cdate,
                "predmet": ccomp,
                "url": curl,
            }
        )
        cmps.sort(key=lambda x: (x["datum"], x["predmet"]), reverse=True)
        with open(tfile, "wt") as fw:
            json.dump(cmps, fw, indent=2, ensure_ascii=False)
