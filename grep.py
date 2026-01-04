import datetime as dt
import json
import os
from urllib.request import urlopen

import lxml.html

URLS = {
    2023: "https://www.praha5.cz/povinne-zverejnovane-informace/prehled-poskytnutych-informaci-podle-zakona-c-106-1999-sb/2023-2/",
    2024: "https://www.praha5.cz/povinne-zverejnovane-informace/prehled-poskytnutych-informaci-podle-zakona-c-106-1999-sb/2024-2/",
    2025: "https://www.praha5.cz/povinne-zverejnovane-informace/prehled-poskytnutych-informaci-podle-zakona-c-106-1999-sb/2025-2/",
    # 2026: "https://www.praha5.cz/povinne-zverejnovane-informace/prehled-poskytnutych-informaci-podle-zakona-c-106-1999-sb/2026-2/",
}

tdir = "data"
os.makedirs(tdir, exist_ok=True)

today = dt.date.today()
this_year = today.year

for year, url in URLS.items():
    # ber jen soucasnej rok + minuly rok, pokud je leden
    if not (year == this_year or (today.month == 1 and this_year - 1 == year)):
        continue

    print(year)

    tfile = os.path.join(tdir, str(year) + ".json")
    # nemuzem dat lxml.html.parse(urlopen(...)), protoze deklarovany content-encoding
    # nereflektuje realitu
    with urlopen(url) as response:
        body = response.read()
        tx = body.decode("utf-8", errors="ignore")
    ht = lxml.html.fromstring(tx)
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
