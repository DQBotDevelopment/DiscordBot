from bs4 import BeautifulSoup
import requests
import pickle
from datetime import datetime

getting = False
url = "https://hiroba.dqx.jp/sc/game/tengoku"

while True:
    now = datetime.now().minute
    if now == 55 and getting == False:
        getting = True
        html = requests.get(url)
        soup = BeautifulSoup(html.content, "html.parser")

        div = soup.find("div", class_="tengoku__period")
        tengoku_statustext = div.text
        tengoku_statustext = "開放されました"
        with open("tengoku.bin", "wb") as f:
            pickle.dump(tengoku_statustext, f)
        
    else:
        getting = False