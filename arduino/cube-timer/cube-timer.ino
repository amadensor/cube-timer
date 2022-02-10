#include <Wire.h>
#include <RTClib.h>

int lcdDevice=52;
int readyLED=3,inspectLED=4,solveLED=5,doneLED=6;
int solveButton=7,resetButton=8;
int beeper=9; //beeper on PWW
int coverDetect=1;
int coverThreshold=110;
unsigned long inspectStart,solveStart,solveFinish;
unsigned long beepStart,beepEnd, beepTimer;
String modes[5]=("Ready","Inspection","Hands Down","Solving","Complete");
String inString,timeString;
int dateYear,dateMonth,dateDay,timeHour,timeMinute,timeSecond;
int inChar;
int mode=4; //start at done
DateTime now;

DS1307 rtc;

void displayInspectTime(){
  Wire.beginTransmission(lcdDevice);
  //calc time string
  Wire.write("timeString");
  Wire.endTransmission();
}

void displaySolveTime(){
  Wire.beginTransmission(lcdDevice);
  //calc time string
  Wire.write("timeString");
  Wire.endTransmission();
}

void saveResults(){
  //write SD
  //Write serial
}

void allOff(){
  digitalWrite(readyLED,LOW);
  digitalWrite(inspectLED,LOW);
  digitalWrite(solveLED,LOW);
  digitalWrite(doneLED,LOW);
}

void setClock(){
  Serial.println("Set Clock");
  inString="";
  while (Serial.available()){
  inChar=Serial.read();
  inString.concat(char(inChar));
  }
  if (inString.substring(0,1)==String('C')){
    dateYear=inString.substring(1,5).toInt();
    dateMonth=inString.substring(5,7).toInt();
    dateDay=inString.substring(7,9).toInt();
    timeHour=inString.substring(9,11).toInt();
    timeMinute=inString.substring(11,13).toInt();
    timeSecond=inString.substring(13,15).toInt();
    now=DateTime(dateYear,dateMonth, dateDay, timeHour, timeMinute, timeSecond);
    rtc.adjust(now);
    Serial.println("Clock set");
  }
}

void setup() {
#ifdef AVR
  Wire.begin();
#else
  Wire1.begin(); // Shield I2C pins connect to alt I2C bus on Arduino Due
#endif
  rtc.begin();
  Serial.begin(9600);
  if (!rtc.begin())
  {
    Serial.println("No RTC");
    Serial.flush();
    rtc.adjust(DateTime(__DATE__, __TIME__));
  }
  now=rtc.now();
  if (now.year()==2000){
    rtc.adjust(DateTime(__DATE__, __TIME__));
  }
  Serial.println(now.hour());
  Serial.println(now.minute());
  Serial.println(now.second());
  Serial.println(now.year());
  Serial.println(now.month());
  Serial.println(now.day());
  Wire.beginTransmission(lcdDevice);
  Wire.write("16X2");
  Wire.endTransmission();
  pinMode(readyLED,OUTPUT);
  pinMode(inspectLED,OUTPUT);
  pinMode(solveLED,OUTPUT);
  pinMode(doneLED,OUTPUT);
  pinMode(solveButton,OUTPUT);
  pinMode(resetButton,OUTPUT);
  pinMode(beeper,OUTPUT);

}
void loop() {
  // put your main code here, to run repeatedly:
  if (mode==0 and analogRead(coverDetect)>coverThreshold){
    mode++;
    inspectStart=millis();
  }
  if (mode==1 and digitalRead(solveButton)==HIGH){
    mode++;
    delay(10);
  }
  if (mode==2 and digitalRead(solveButton)==LOW){
    mode++;
    solveStart=millis();
    allOff();
    digitalWrite(solveLED,HIGH);
  }
  if (mode==3 and digitalRead(solveButton)==HIGH){
    mode++;
    allOff();
    digitalWrite(doneLED,HIGH);
  }
  if (mode==4 and analogRead(coverDetect)<coverThreshold and digitalRead(resetButton)==HIGH){
    mode=0;
    allOff();
    digitalWrite(readyLED,HIGH);
    saveResults();
  }
  if (mode==1){
    displayInspectTime();
    beepTimer=millis()- inspectStart;
    if (beepTimer > beepStart and beepTimer < beepEnd){
      digitalWrite(beeper,HIGH);
    }
    else {
      digitalWrite(beeper,LOW);
    }
  }
  if (mode==3){
    displaySolveTime();
  }

}
