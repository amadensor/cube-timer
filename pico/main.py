import sys
import os
import select
import machine
import time
import json
import ds1307
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

SDA=machine.Pin(0)
SCL=machine.Pin(1)

readyLEDnum=8
inspectLEDnum=10
solveLEDnum=13
doneLEDnum=15

solveButtonnum=17
resetButtonnum=18
beepernum=20 #beeper on PWW
beeper=machine.PWM(machine.Pin(20))
beeper.freq(1500)

coverDetect=machine.ADC(26)

readyLED=machine.Pin(readyLEDnum,machine.Pin.OUT)
inspectLED=machine.Pin(inspectLEDnum,machine.Pin.OUT)
solveLED=machine.Pin(solveLEDnum,machine.Pin.OUT)
doneLED=machine.Pin(doneLEDnum,machine.Pin.OUT)


solveButton=machine.Pin(solveButtonnum,machine.Pin.IN)
resetButton=machine.Pin(resetButtonnum,machine.Pin.IN)


modeNum=4
penalty="F"
coverThreshold=1000
inspectLimit=15000
inspectFail=17000
cutOff=600000
inspectStart=0
solveStart=0
solveFinish=0
beepTimer=0
alertOne=8000
alertTwo=12000
dateYear=0
dateMonth=0
dateDay=0
timeHour=0
timeMinute=0
timeSecond=0
inChar=0
lcd_addr=0x27
i2c=machine.I2C(0,sda=SDA,scl=SCL)
rtc=ds1307.DS1307(i2c)

lcdDisplay=I2cLcd(i2c,lcd_addr,4,20)

"""filePath=(
    str(rtc.datetime()[0])+
    "/"+
    str(rtc.datetime()[1])+
    "/"+
    str(rtc.datetime()[2])+
    "/"+
    str(rtc.datetime()[3])+
    "/"+
    str(rtc.datetime()[4])+
    "/"+
    str(rtc.datetime()[5])+
    "/"+
    "scores.csv"
)"""

filePath="scores.csv"
penalty
try:
    scoreFile=open(filePath,"a")
except:
    scoreFile=open(filePath,"w")
    fileData="Time Stamp,Inspect Time, Solve Time,Penalty, Inspect Start, Solve Start, Solve Finish\n"
    scoreFile.write(fileData)

def displayInspectTime():
    global solveStart, solveFinish, penalty
    inspectTime=0
    lcdDisplay.move_to(0,0)
    inspectTime=(time.ticks_ms()-inspectStart)/1000.0
    lcdDisplay.putstr(str(inspectTime))
    if (inspectLimit>0 and (inspectTime)>(inspectLimit/1000)):
        penalty="T"
    if inspectTime>(inspectFail/1000):
        print(inspectTime,inspectFail)
        solveStart=time.ticks_ms()
        solveFinish=time.ticks_ms()
        failSolve()

def failSolve():
    allOff()
    modeNum=4
    penalty="DNF"
    saveResults()
    lcdDisplay.clear()
    lcdDisplay.move_to(0,0)
    lcdDisplay.putstr("DNF")

def displaySolveTime():
    global solveFinish
    solveTime=0
    lcdDisplay.move_to(0,0)
    solveTime=(time.ticks_ms()-solveStart)/1000.0
    if solveTime>(cutOff/1000):
        solveFinish=time.ticks_ms()
        failSolve()
    else:
        lcdDisplay.putstr(str(solveTime))


def formatTime(now):
    dttmStr=""
    dttmStr=dttmStr+str(now[4])
    dttmStr=dttmStr+(":")
    if now[5] < 10:
        dttmStr=dttmStr+("0")
    dttmStr=dttmStr+str(now[5])
    dttmStr=dttmStr+(":")
    if now[6] < 10:
        dttmStr=dttmStr+"0"
    dttmStr=dttmStr+str(now[6])
    dttmStr=dttmStr+(" ")
    dttmStr=dttmStr+str(now[1])
    dttmStr=dttmStr+("/")
    dttmStr=dttmStr+str(now[2])
    dttmStr=dttmStr+("/")
    dttmStr=dttmStr+str(now[0])
    return dttmStr


def displayCurrentTime():
    now=rtc.datetime()
    lcdDisplay.move_to(0,1)
    lcdDisplay.putstr(formatTime(now))


def saveResults():
    #write SD
    #Write serial
    global scoreFile
    inspectTime=0
    solveTime=0
    inspectTime=(solveStart-inspectStart)/1000.0
    solveTime=(solveFinish-solveStart)/1000.0
    lcdDisplay.clear()
    lcdDisplay.move_to(0,0)
    lcdDisplay.putstr("Inspect: ")
    lcdDisplay.putstr(str(inspectTime))
    lcdDisplay.move_to(0,1)
    lcdDisplay.putstr("Solve: ")
    lcdDisplay.putstr(str(solveTime))
    if penalty=="T":
        lcdDisplay.move_to(15,1)
        lcdDisplay.putstr("+")
    fileData=(
        formatTime(rtc.datetime())+
        ","+
        str(inspectTime)+
        ","+
        str(solveTime)+
        ","+
        penalty+
        ","+
        str(inspectStart)+
        ","+
        str(solveStart)+
        ","+
        str(solveFinish)+
        "\n"
        )
    scoreFile.write(fileData)
    scoreFile.flush()

def send_sd():
    """send sd content to """
    sd=open("scores.csv")
    for line in sd.readlines():
        print(line)

def allOff():
    readyLED.off()
    inspectLED.off()
    solveLED.off()
    doneLED.off()

def processCommands():
    print("Commands")
    inString=""
    cmd=""
    val=""
    inString=readSerial()

    for t in range(0,len(inString)):
        if inString[t]==':':
            cmd=inString[:t]
            cmd.strip()
            t+=1
            val=inString[t:].strip()

    #Serial.println(cmd);
    #Serial.println(val);
    if cmd=="alert1":
        alertOne=val.toInt()*1000.0
    if cmd=="alert2":
        alertTwo=val.toInt()*1000.0
    if cmd=="inspect":
        inspectLimit=val.toInt()*1000.0
    if cmd=="cutoff":
        cutOff=val.toInt()*1000.0
    if cmd=="fail":
        inspectFail=val.toInt()*1000.0
    if cmd=="rs":
        send_scores()
    if cmd=="sd":
        send_sd()
    if cmd=="clock":
        setClock(val)


def send_scores():
    scoreJSON={
        "Inspection Limit":inspectLimit,
        "Inspect Time":solveStart-inspectStart,
        "Solve Time":solveFinish-solveStart}
    print (json.dumps(scoreJSON))

def readSerial():
    retString=""
    time.sleep_ms(500)
    
    for line in sys.stdin.readline().strip():
        retString=retString+line
    print("read",retString)
    return retString


def setClock(inString):
    #Serial.println("Set Clock");
    if inString[0:1]=='C':
        dateYear=int(inString[1:5])
        dateMonth=int(inString[5:7])
        dateDay=int(inString[7:9])
        timeHour=int(inString[9:11])
        timeMinute=int(inString[11:13])
        timeSecond=int(inString[13:15])
        rtc.datetime((dateYear,dateMonth, dateDay, 0, timeHour, timeMinute, timeSecond,0))
        print(inString)
        print("Clock set")
        print(rtc.datetime())

def setup():
    global scoreFile
    fileData=""

    lcdDisplay.clear()
    lcdDisplay.backlight_on()
    try:
      os.stat("CONF.TXT")
      exists=1
    except:
      exists=0
    if exists:
        confFile=open("CONF.TXT","r")
        fileData=""
        while confFile.available():
            inChar=confFile.read()
            fileData.concat(char(inChar))
        confFile.close()
        n=0
        confStrings=[]
        for t in range(0,len(fileData)):
            if fileData.charAt(t)==',':
                n+=1
            else:
                confStrings[n].concat(fileData.charAt(t))
        cutOff=(confStrings[0].toInt())*1000
        inspectLimit=(confStrings[1].toInt())*1000
        inspectFail=(confStrings[2].toInt())*1000
        alertOne=(confStrings[3].toInt())*1000
        alertTwo=(confStrings[4].toInt())*1000
    #print(now.hour())
    #print(now.minute())
    #print(now.second())
    #print(now.year())
    #print(now.month())
    #print(now.day())
    allOff()
    lcdDisplay.move_to(0,1)
    lcdDisplay.putstr("Boot Complete")

def main_loop():
    global modeNum, penalty, inspectStart, solveFinish, solveStart
    modes=["Ready","Inspection","Hands Down","Solving","Complete","DNF"]
    if (select.select([sys.stdin],[],[],0))[0]:
        processCommands()
    if (modeNum==0 and coverDetect.read_u16()>coverThreshold):
        modeNum=modeNum+1
        if inspectLimit==0:
            modeNum=modeNum+1
        else:
            lcdDisplay.clear()
            lcdDisplay.move_to(0,2)
            allOff()
            inspectLED.on()
            lcdDisplay.putstr(modes[modeNum])
        inspectStart=time.ticks_ms()
    if (modeNum==1 and solveButton.value()):
        modeNum=modeNum+1
        time.sleep_ms(10)
        lcdDisplay.clear()
        lcdDisplay.move_to(0,2)
        lcdDisplay.putstr(modes[modeNum])
    if modeNum==2 and solveButton.value()==0:
        modeNum=modeNum+1
        solveStart=time.ticks_ms()
        allOff()
        lcdDisplay.clear()
        solveLED.on()
        lcdDisplay.move_to(0,2)
        lcdDisplay.putstr(modes[modeNum])
    if (modeNum==3 and solveButton.value()):
        modeNum=modeNum+1
        solveFinish=time.ticks_ms()
        allOff()
        doneLED.on()
        lcdDisplay.move_to(0,2)
        lcdDisplay.putstr(modes[modeNum])
        saveResults()
    if modeNum==4:
        blinkTime=int(time.ticks_ms()/1000)
        if (blinkTime/2.00)==int(blinkTime/2.00):
            doneLED.on()
        else:
            if (penalty != "F"):
                doneLED.off()
    if (modeNum==4 and coverDetect.read_u16()<coverThreshold and resetButton.value()):
        modeNum=0
        allOff()
        penalty="F"
        readyLED.on()
        lcdDisplay.move_to(0,2)
        lcdDisplay.putstr(modes[modeNum])
        lcdDisplay.clear()
        lcdDisplay.move_to(0,0)
        lcdDisplay.putstr("Ready")
    if (modeNum==1 or modeNum==2):
        displayInspectTime()
        beepTimer=time.ticks_ms()- inspectStart
        if ((alertOne < beepTimer) and (beepTimer < alertOne + 200)
        or (alertTwo < beepTimer) and (beepTimer < alertTwo + 200)
        or (inspectLimit < beepTimer) and (beepTimer < inspectLimit + 200)
        ):
            beeper.duty_u16(20000)
        else:
            beeper.duty_u16(0)
    if (modeNum==3):
        displaySolveTime()
    if (modeNum==0):
        displayCurrentTime()

setup()

while True:
  main_loop()
