#include <LCD_I2C.h>
//#include <Wire.h>
#include <RTClib.h>

LCD_I2C lcdDisplay(0x27,16,2);
int readyLED=3,inspectLED=4,solveLED=5,doneLED=6;
int solveButton=7,resetButton=8;
int beeper=9; //beeper on PWW
int coverDetect=1;
int coverThreshold=300;
unsigned long inspectStart,solveStart,solveFinish;
unsigned long beepTimer, alertOne=8000, alertTwo=12000;
String modes[5]={"Ready","Inspection","Hands Down","Solving","Complete"};
int dateYear,dateMonth,dateDay,timeHour,timeMinute,timeSecond;
int inChar;
int mode=4; //start at done
DateTime now;

DS1307 rtc;

void displayInspectTime(){
  float inspectTime;
  lcdDisplay.setCursor(0,0);
  inspectTime=(millis()-inspectStart)/1000.0;
  lcdDisplay.print(inspectTime);
}

void displaySolveTime(){
  float solveTime;
  lcdDisplay.setCursor(0,0);
  solveTime=(millis()-solveStart)/1000.0;
  lcdDisplay.print(solveTime);
}

void saveResults(){
  //write SD
  //Write serial
  float inspectTime, solveTime;
  inspectTime=(solveStart-inspectStart)/1000.0;
  solveTime=(solveFinish-solveStart)/1000.0;
  lcdDisplay.clear();
  lcdDisplay.setCursor(0,0);
  lcdDisplay.print("Inspect: ");
  lcdDisplay.print(inspectTime);
  lcdDisplay.setCursor(0,1);
  lcdDisplay.print("Solve: ");
  lcdDisplay.print(solveTime);
}

void allOff(){
  digitalWrite(readyLED,LOW);
  digitalWrite(inspectLED,LOW);
  digitalWrite(solveLED,LOW);
  digitalWrite(doneLED,LOW);
}

String readSerial(){
  int inChar;
  String retString="";
  delay(500);
  while(Serial.available()){
    inChar=Serial.read();
    retString.concat(char(inChar));
  }
  return retString;
}

void setClock(){
  String inString;
  Serial.println("Set Clock");
  inString=readSerial();
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
  //Wire.begin();
#else
  //Wire1.begin(); // Shield I2C pins connect to alt I2C bus on Arduino Due
#endif
  lcdDisplay.begin();
  lcdDisplay.backlight();
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
  //Serial.println(analogRead(coverDetect));
  //delay(1000);
  if (mode==0 and analogRead(coverDetect)>coverThreshold){
    mode++;
    inspectStart=millis();
    lcdDisplay.clear();
    Serial.print(mode);
    Serial.println(modes[mode]);
  }
  if (mode==1 and digitalRead(solveButton)==HIGH){
    mode++;
    delay(10);
    lcdDisplay.clear();
    Serial.print(mode);
    Serial.println(modes[mode]);
  }
  if (mode==2 and digitalRead(solveButton)==LOW){
    mode++;
    solveStart=millis();
    allOff();
    lcdDisplay.clear();
    digitalWrite(solveLED,HIGH);
    Serial.print(mode);
    Serial.println(modes[mode]);
  }
  if (mode==3 and digitalRead(solveButton)==HIGH){
    mode++;
    solveFinish=millis();
    allOff();
    digitalWrite(doneLED,HIGH);
    Serial.print(mode);
    Serial.println(modes[mode]);
    saveResults();    
  }
  if (mode==4 and analogRead(coverDetect)<coverThreshold and digitalRead(resetButton)==HIGH){
    mode=0;
    allOff();
    digitalWrite(readyLED,HIGH);
    Serial.print(mode);
    Serial.println(modes[mode]);
    lcdDisplay.clear();
    lcdDisplay.setCursor(0,0);
    lcdDisplay.print("Ready");
  }
  if (mode==1){
    displayInspectTime();
    beepTimer=millis()- inspectStart;
    if ((alertOne < beepTimer) && (beepTimer < alertOne + 200)){
      digitalWrite(beeper,HIGH);
      Serial.print("beep");
      Serial.print(alertOne);
      Serial.print(":");
      Serial.print(beepTimer);
      Serial.print(":");
      Serial.println(alertOne + 200);
    }
    else {
      digitalWrite(beeper,LOW);
      //Serial.println("no beep");
    }
  }
  if (mode==3){
    displaySolveTime();
  }

}
