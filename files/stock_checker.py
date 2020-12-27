#!/usr/bin/env python3

import pandas as pd
import requests
from bs4 import BeautifulSoup
import yeelight.transitions
from yeelight import *
from yeelight import discover_bulbs, Bulb
from yeelight import Flow, transitions
from yeelight.flow import Action
from multiprocessing import Process
import pandas as pd
import time
import requests
import sys

def setupStockAvailableFlow(bulbIp, durationFlowSeconds=60):
  try:
    bulb = Bulb(bulbIp)

    durationPulseInMs=200
    count = (durationFlowSeconds * 1000) / durationPulseInMs
    transitionsP = yeelight.transitions.pulse(0, 255, 0, durationPulseInMs, 100)
    flow = Flow(
        count=count,
        action=Action.recover,
        transitions=transitionsP
    )
    bulb.turn_on()
    bulb.start_flow(flow)
# except:
#   print("Error setting flow in bulb",file=sys.stderr)
  except Exception as ex:
    logging.exception("Something awful happened!")

# starts thread
def startStockAvailableAlert():
    bulbs = discover_bulbs()
    for b in bulbs:
       print("starting {}".format(b['ip']))
       bulbIp = b['ip']
       print(f"bulbIp:{bulbIp}")
       p = Process(target=setupStockAvailableFlow, args=(bulbIp,))
       p.start()
       p.join()


def checkForStock(page):
    # soup = BeautifulSoup(wd.page_source)
    soup = BeautifulSoup(page.content,features="html.parser")
    items = soup.find("div", {"class": "items-grid-view"})

    items_processed = []

    for row in items.findAll("div"):
        row_processed = []
        itemTitle = row.find("a", {"class": "item-title"})
        itemPromoText = row.find("p", {"class": "item-promo"})

        status = "Available"

        if itemPromoText and itemPromoText.text == "OUT OF STOCK":
            status = "Sold Out"

        if itemTitle:
            row_processed.append(itemTitle.text)
            row_processed.append(status)

        if row_processed:
            items_processed.append(row_processed)
    # cells[3].find("img")["src"]
    # columns = ["ImageUrl","Origin"]

    df = pd.DataFrame.from_records(items_processed, columns=["Item Title", "Status"])

    return df



if __name__ == '__main__':
    print("Main line start")
    # search for RTX 3000 series
    URL_NVIDIA_RTX_PAGE1 = 'https://www.newegg.com/p/pl?N=101582767%20601357282'
    URL_NVIDIA_RTX_PAGE2 = 'https://www.newegg.com/p/pl?N=101582767%20601357282&page=2'
    URL_RYZEN_5000SERIES = "https://www.newegg.com/p/pl?N=101582716%2050001028%20601359163"
    URL_RYZEN_THREADRIPPER = "https://www.newegg.com/p/pl?N=100007671%20601350560"

    STOCK_URLS=[URL_NVIDIA_RTX_PAGE1, URL_NVIDIA_RTX_PAGE2, URL_RYZEN_5000SERIES]

    for url in STOCK_URLS:
      page = requests.get(url)
      stock_df = checkForStock(page)
      print(stock_df)
      if "Available" in stock_df.Status.values:
        print("Stock Available!")
        # Switch on lighting to alert
        startStockAvailableAlert()
        break
      else:
        print("Everything out of stock!")
      time.sleep(5)
    print("Main line end")
