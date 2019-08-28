import discord
from discord.ext import commands
from discord.ext import tasks
from datetime import datetime, timedelta
import csv

from bs4 import BeautifulSoup
import requests
import pickle

#自分用の時間class
class MyDataTime:
    Month = 1
    Day = 1
    Hour = 0
    Minute = 0

    def __init__(self, InMouth,InDay,InHour,InMinute):
        self.Month = InMouth
        self.Day = InDay
        self.Hour = InHour
        self.Minute = InMinute

    def IsEqual(left,right):
        return (left.Month == right.Month) and (left.Day == right.Day) and (left.Hour == right.Hour) and (left.Minute == right.Minute)

class NoticeMessage:
    Text = ""
    ChannelID = -1
    def __init__(self,InText,InChannelID):
        self.Text = InText
        self.ChannelID = InChannelID
    

#通知を行うリスト
class NoticeBase:
    time = MyDataTime(1,1,0,0)
    Message = NoticeMessage("",-1)
    def __init__(self, InTime,InText,InChannelID):
        #文字列を時間に変更する
        InTimeSize = len(InTime.split(":"))
        TimeList = []
        TimeList.append(datetime.now().month)
        TimeList.append(datetime.now().day)
        TimeList.append(datetime.now().hour)
        TimeList.append(datetime.now().minute)
        for i in range(len(TimeList)):
            if 0 <= i - InTimeSize:
                TimeList[i] = int(InTime.split(":")[i - InTimeSize])
        self.time = MyDataTime(TimeList[0],TimeList[1],TimeList[2],TimeList[3])
        self.Message = NoticeMessage(InText,InChannelID)

class NoticeSystem:
    NoticeList = []

    #通知を追加する
    def Add(self,time,text,channelid):
        self.NoticeList.append(NoticeBase(time,text,channelid))
    def GetNowTimeText(self):
        #月日時分秒
        nowTime = MyDataTime(datetime.now().month,datetime.now().day,datetime.now().hour,datetime.now().minute)
        ReturnList = []
        DeleteIndex = []
        for i in range(len(self.NoticeList)):
            if MyDataTime.IsEqual(self.NoticeList[i].time,nowTime):
                ReturnList.append(self.NoticeList[i].Message)
                DeleteIndex.append(i)
                break
        for Index in DeleteIndex:
            self.NoticeList.pop(Index)
        return ReturnList

#通知システム
MyNoticeSystem = NoticeSystem()

#コンフィグファイルのパス
FilePath = "config/Config.ini"

with open(FilePath) as f:
    ConfigLine = f.readlines()

#トークン
TOKEN = ConfigLine[0].strip("\n")

DefencePath = 'datatable/Defence.csv'
BossLevelPath = 'datatable/BossLevel.csv'
D_PopPath = 'datatable/d_pop.csv'
HelpPath = 'config/help.bin'

#天獄
tengokuurl = "https://hiroba.dqx.jp/sc/game/tengoku"
tengokufileReading = False

#Botのコマンドの指定（うまく起動できていない）
bot = commands.Bot(command_prefix='!')

#防衛軍スケジュールを開く
def OpenDefence():
    with open(DefencePath,'r') as fp:
        return list(csv.reader(fp))

#エンドボスのレベルテーブルを開く
def OpenBossLevel():
    with open(BossLevelPath,'r') as fp:
        return list(csv.reader(fp))
#防衛軍タイムスケジュールを開く
def OpenD_Pop():
    with open(D_PopPath,'r') as fp:
        return list(csv.reader(fp))
def OpenD_PopTable(path):
    with open(path,'r') as fp:
        return list(csv.reader(fp))

#天獄が開いているかをチェックする
def Check_tengoku():
    tengokutext = BeautifulSoup(requests.get(tengokuurl).content,"html.parser").find("div",class_="tengoku__period").text
    if tengokutext.find("現在開放されていません") >= 0:
        return False
    else:
        return tengokutext

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

@tasks.loop(seconds=1)
async def tengokuloop():
    nowmin = datetime.now().minute
    channel = client.get_channel(607853240272551959)
    if nowmin >= 0:
        tengokufileReading = True
        with open("tengoku.bin","rb") as f:
            text = pickle.load(f)
            print(text)
        if text.find("現在開放されていません") >= 0:
            return
        else:
            await channel.send(text)
    else:
        tengokufileReading = False


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
        with open(HelpPath) as f:
           await message.channel.send(f.read())
        return

    if message.content == '/tengoku':
        await message.channel.send(Check_tengoku())

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
    tengokuloop.start()

#ループのスタート
#loop.start()
#クライアントを走らせる
client.run(TOKEN)

