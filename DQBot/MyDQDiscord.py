import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta
from NoticeSystem import NoticeSystem
from NoticeSystem import NoticeMessage
import csv

from bs4 import BeautifulSoup
import requests
import pickle

class TengokuNotice(commands.Cog):
    URL = "https://hiroba.dqx.jp/sc/game/tengoku"

    def __init__(self):
        self.channel = 0
        self.open = False
        self.delta = 0

    def Set_ch(self,ch : discord.channel):
        self.channel = ch

    @tasks.loop(seconds=30)
    async def Update(self):
        now = datetime.now()
        if now.minute >= 0 and now.minute <= 5 and self.open == False:
            soup = BeautifulSoup(requests.get(TengokuNotice.URL).content,"html.parser")
            div = soup.find("div", class_="tengoku__period")
            tengokutext = div.text

            if tengokutext.find("現在開放されていません") >= 0:
                return
            else:
                self.delta = now
                self.open = True
                await self.channel.send("天獄情報" + tengokutext)
        elif self.open and (now - self.delta).day >= 3:
            self.open = False

#通知システム
MyNoticeSystem = NoticeSystem()

#天獄通知システム
tengoku = TengokuNotice()

#コンフィグファイルのパス
FilePath = "config/Config.ini"

with open(FilePath,encoding="utf-8") as f:
    ConfigLine = f.readlines()

#トークン
TOKEN = ConfigLine[0].strip("\n")

DefencePath = 'datatable/Defence.csv'
BossLevelPath = 'datatable/BossLevel.csv'
D_PopPath = 'datatable/d_pop.csv'
HelpPath = 'config/help.bin'

#Botのコマンドの指定（うまく起動できていない）
bot = commands.Bot(command_prefix='!')

#防衛軍スケジュールを開く
def OpenDefence():
    with open(DefencePath,'r',encoding="utf-8") as fp:
        return list(csv.reader(fp))

#エンドボスのレベルテーブルを開く
def OpenBossLevel():
    with open(BossLevelPath,'r',encoding="utf-8") as fp:
        return list(csv.reader(fp))
#防衛軍タイムスケジュールを開く
def OpenD_Pop():
    with open(D_PopPath,'r',encoding="utf-8") as fp:
        return list(csv.reader(fp))
def OpenD_PopTable(path):
    with open(path,'r',encoding="utf-8") as fp:
        return list(csv.reader(fp))

#クライアント情報
client = discord.Client()


#loop処理
@tasks.loop(seconds=1)
async def loop():
    now = datetime.now().strftime('%m:%d:%H:%M:%S')
    NoticeMessageTextList = MyNoticeSystem.GetNowTimeText()
    if len(NoticeMessageTextList) > 0:
        text = "予約通知\n" + now + "\n"
        for message in NoticeMessageTextList:
            channel = client.get_channel(message.ChannelID)
            await channel.send(text + message.Text + "\n")
        return

#メッセージが来た時のイベント
@client.event
async def on_message(message):
    #自分の発言には反応しない
    if message.author == client.user:
        return
    #防衛軍情報をメッセージ送信する
    if message.content == '/defence':
        lst = OpenDefence()
        line = lst[datetime.now().weekday()]
        text = datetime.now().strftime("[%m/%d %H:%M:%S]\n")
        text += "現在の防衛軍\n"
        text += line[datetime.now().hour] + "\n"
        text += "今日の防衛軍\n\n"
        for i in range(len(line)):
            text += str(i) + "時 : " + line[i] + "\n"
        await message.channel.send(text)
        return
    #ボスレベルをメッセージ送信する
    if message.content == "/bosslevel":
        lst = OpenBossLevel()
        #一番上は基準となる時間データが入っている
        StandardTime = datetime(int(lst[0][0]),int(lst[0][1]),int(lst[0][2]))
        #現在の時間から標準時間を引いてその差で今日の強さを求める（ドラクエⅩは翌日６時更新のため６時間分マイナスする）
        days = (datetime.now() - timedelta(hours = 6) - StandardTime).days
        text = datetime.now().strftime("[%m/%d %H:%M:%S]\n")
        text += "今日のつよさ\n"
        num = 1
        while num < len(lst):
            text += lst[num][0] + ":" + str((days + int(lst[num][2])) % int(lst[num][1]) + 1) + "\n"
            num += 1
        await message.channel.send(text)
        return
    #防衛軍出現情報をメッセージ送信する
    if message.content.split(" ", 1)[0] == "/d_pop":
        bosstype = message.content.split(" ",1)[1]
        lst = OpenD_Pop()
        text = ""
        enemyPath = ""
        itemPath = ""

        for line in lst:
            if line[0] == bosstype:
                enemyPath = line[1]
                itemPath = line[2]
                break

        if enemyPath == "" or itemPath == "":
            return

        enemylst = OpenD_PopTable(enemyPath)
        itemlst = OpenD_PopTable(itemPath)
        text += "敵出現タイムテーブル\n"
        for eneline in enemylst:
            text += eneline[0] + " : " + eneline[1] + " : " + eneline[2] + "\n"
        text += "\nアイテム出現タイムテーブル\n"
        for iteline in itemlst:
            text += iteline[0] + " : " + iteline[1] + " : " + iteline[2] + "\n"
        await message.channel.send(text)
        return
    if message.content.split(" ",2)[0] == "/notice":
        print(message.content)
        MyNoticeSystem.Add(message.content.split(" ",2)[1],message.content.split(" ",2)[2],message.channel.id)
        return
    #ヘルプを表示する
    if message.content == "/help":
        with open(HelpPath,encoding="utf-8") as f:
           await message.channel.send(f.read())
        return

#コマンド動作のbot（うまく動いていない）
@bot.command()
async def defence():
    channel = client.get_channel(CHANNEL_ID)
    if channel != None:
        lst = OpenDQX()
        line = lst[datetime.now().weekday()]
        text = datetime.now().strftime("[%m/%d %H:%M:%S]\n")
        text += "現在の防衛軍\n"
        text += line[datetime.now().hour] + "\n"
        text += "今日の防衛軍\n\n"
        for i in range(len(line)):
            text += str(i) + "時:" + line[i] + "\n"
        await channel.send(text)

#接続完了イベント
@client.event
async def on_connect():
    loop.start()
    tengoku.Set_ch(client.get_channel(607614417999233034))
    tengoku.Update.start()

#クライアントを走らせる
client.run(TOKEN)

