from datetime import datetime, timedelta

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