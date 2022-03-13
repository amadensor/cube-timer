//#include <SPI.h>
#include <SD.h>
#include <LCD_I2C.h>
//#include <Wire.h>
#include <RTClib.h>

LCD_I2C lcdDisplay(0x27,16,2);
int readyLED=3,inspectLED=4,solveLED=5,doneLED=6;
int solveButton=7,resetButton=8;
int beeper=9; //beeper on PWW
int coverDetect=1;
int coverThreshold=300;
int validSD=0;
unsigned long inspectLimit=15000,inspectFail=17000,cutOff=600000;
unsigned long inspectStart,solveStart,solveFinish;
unsigned long beepTimer, alertOne=8000, alertTwo=12000;
int dateYear,dateMonth,dateDay,timeHour,timeMinute,timeSecond;
int inChar;
int mode=4; //start at done
DateTime now;
File scoreFile;
String fileData,filePath;
String penalty="F";

DS1307 rtc;

void displayInspectTime(){
  float inspectTime;
  lcdDisplay.setCursor(0,0);
  inspectTime=(millis()-inspectStart)/1000.0;
  lcdDisplay.print(inspectTime);
  if (inspectLimit>0 && (inspectTime)>(inspectLimit/1000)){
    penalty="T";
  }
  if (inspectTime>(inspectFail/1000)) {
    solveStart=millis();
    solveFinish=millis();
    failSolve();
  }
 }

void failSolve(){
    allOff();
    mode=4;
    penalty="DNF";
    saveResults();
    lcdDisplay.clear();
    lcdDisplay.setCursor(0,0);
    lcdDisplay.print("DNF");
}
void displaySolveTime(){
  float solveTime;
  lcdDisplay.setCursor(0,0);
  solveTime=(millis()-solveStart)/1000.0;
  if (solveTime>(cutOff/1000)) {
    solveFinish=millis();
    failSolve();
  }
  else lcdDisplay.print(solveTime);
}

String formatTime(DateTime dttm){
  String dttmStr="";
  dttmStr.concat(now.hour());
  dttmStr.concat(":");
  if (now.minute() < 10) dttmStr.concat("0");
  dttmStr.concat(now.minute());
  dttmStr.concat(":");
  if (now.second() < 10) dttmStr.concat("0");
  dttmStr.concat(now.second());
  dttmStr.concat(" ");
  dttmStr.concat(now.month());
  dttmStr.concat("/");
  dttmStr.concat(now.day());
  dttmStr.concat("/");
  dttmStr.concat(now.year());
  return dttmStr;
}

void displayCurrentTime(){
  now=rtc.now();
  lcdDisplay.setCursor(0,1);
  lcdDisplay.print(formatTime(now));
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
  if (penalty=="T"){
    lcdDisplay.setCursor(15,1);
    lcdDisplay.print("+");
  }
  if (validSD==1)
  {
    fileData="";
    fileData.concat(formatTime(rtc.now()));
    fileData.concat(",");
    fileData.concat(inspectTime);
    fileData.concat(",");
    fileData.concat(solveTime);
    fileData.concat(",");
    fileData.concat(penalty);
    fileData.concat(",");
    fileData.concat(inspectStart);
    fileData.concat(",");
    fileData.concat(solveStart);
    fileData.concat(",");
    fileData.concat(solveFinish);
    scoreFile.println(fileData);
    scoreFile.flush();
  }
}

void allOff(){
  digitalWrite(readyLED,LOW);
  digitalWrite(inspectLED,LOW);
  digitalWrite(solveLED,LOW);
  digitalWrite(doneLED,LOW);
}
void processCommands(){
  String inString,cmd,val;
  inString=readSerial();

  for (int t=0;t<inString.length();t++)
  {
    if (inString.charAt(t)==':'){
      cmd=inString.substring(0,t);
      cmd.trim();
      t++;
      val=inString.substring(t,inString.length());
      val.trim();
    }
  }

  //Serial.println(cmd);
  //Serial.println(val);
  if (cmd=="alert1") alertOne=val.toInt()*1000.0;
  if (cmd=="alert2") alertTwo=val.toInt()*1000.0;
  if (cmd=="inspect") inspectLimit=val.toInt()*1000.0;
  if (cmd=="rs")
  {
    send_scores();
  }
  if (cmd=="clock") setClock(val);
}

void send_scores(){
  String scoreJSON;
  scoreJSON.concat("{\"Inspection Limit\":");
  scoreJSON.concat(inspectLimit);
  scoreJSON.concat(",\"Inspect Time\":");
  scoreJSON.concat(solveStart-inspectStart);
  scoreJSON.concat(",\"Solve Time\":");
  scoreJSON.concat(solveFinish-solveStart);
  scoreJSON.concat("}");
  Serial.println(scoreJSON);
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

void setClock(String inString){
  //Serial.println("Set Clock");
  if (inString.substring(0,1)==String('C')){
    dateYear=inString.substring(1,5).toInt();
    dateMonth=inString.substring(5,7).toInt();
    dateDay=inString.substring(7,9).toInt();
    timeHour=inString.substring(9,11).toInt();
    timeMinute=inString.substring(11,13).toInt();
    timeSecond=inString.substring(13,15).toInt();
    now=DateTime(dateYear,dateMonth, dateDay, timeHour, timeMinute, timeSecond);
    rtc.adjust(now);
    //Serial.println("Clock set");
    Serial.println(now.hour());
    Serial.println(now.minute());
    Serial.println(now.second());
    Serial.println(now.year());
    Serial.println(now.month());
    Serial.println(now.day());
  }
}

void setup() {
  String fileData;
  File confFile;

#ifdef AVR
  //Wire.begin();
#else
  //Wire1.begin(); // Shield I2C pins connect to alt I2C bus on Arduino Due
#endif
  lcdDisplay.begin();
  lcdDisplay.backlight();
  Serial.begin(9600);
  if (!rtc.begin())
  {
    //Serial.println("No RTC");
    //Serial.flush();
    rtc.adjust(DateTime(__DATE__, __TIME__));
  }
  now=rtc.now();
  if (now.year()==2000){
    rtc.adjust(DateTime(__DATE__, __TIME__));
  }
  SD.begin();
  if(SD.exists("CONF.TXT"))
  {
    confFile=SD.open("CONF.TXT");
    fileData="";
    while (confFile.available())
    {
      inChar=confFile.read();
      fileData.concat(char(inChar));
    }
    confFile.close();
    int n=0;
    String confStrings[6];
    for (int t=0;t<=fileData.length();t++){
      if (fileData.charAt(t)==','){
        n++;
      }
      else{
        confStrings[n].concat(fileData.charAt(t));
      }
    }
    cutOff=(confStrings[0].toInt())*1000;
    inspectLimit=(confStrings[1].toInt())*1000;
    inspectFail=(confStrings[2].toInt())*1000;
    alertOne=(confStrings[3].toInt())*1000;
    alertTwo=(confStrings[4].toInt())*1000;
    lcdDisplay.setCursor(0,0);
    lcdDisplay.print("SD Card OK");
    validSD=1;
    filePath="";
    filePath.concat(now.year());
    filePath.concat("/");
    filePath.concat(now.month());
    filePath.concat("/");
    filePath.concat(now.day());
    filePath.concat("/");
    filePath.concat(now.hour());
    filePath.concat("/");
    filePath.concat(now.minute());
    filePath.concat("/");
    filePath.concat(now.second());
    filePath.concat("/");
    SD.mkdir(filePath);
    filePath.concat("scores.csv");
    scoreFile=SD.open(filePath,FILE_WRITE);
    fileData="Time Stamp,Inspect Time, Solve Time,Penalty, Inspect Start, Solve Start, Solve Finish";
    scoreFile.println(fileData);
    scoreFile.flush();
  }
  else
  {
    lcdDisplay.setCursor(0,0);
    lcdDisplay.print("No valid SD");
  }
  //Serial.println(now.hour());
  //Serial.println(now.minute());
  //Serial.println(now.second());
  //Serial.println(now.year());
  //Serial.println(now.month());
  //Serial.println(now.day());
  pinMode(readyLED,OUTPUT);
  pinMode(inspectLED,OUTPUT);
  pinMode(solveLED,OUTPUT);
  pinMode(doneLED,OUTPUT);
  pinMode(solveButton,OUTPUT);
  pinMode(resetButton,OUTPUT);
  pinMode(beeper,OUTPUT);
  lcdDisplay.setCursor(0,1);
  lcdDisplay.print("Boot Complete");
}
void loop() {
  String modes[6]={"Ready","Inspection","Hands Down","Solving","Complete","DNF"};
  if (Serial.available()) processCommands();
  if (mode==0 and analogRead(coverDetect)>coverThreshold){
    mode++;
    if (inspectLimit==0)
    {
      mode++;
    }
    else
    {
      lcdDisplay.clear();
      lcdDisplay.setCursor(0,2);
      allOff();
      digitalWrite(inspectLED,HIGH);
      lcdDisplay.print(modes[mode]);
    }
    inspectStart=millis();
  }
  if (mode==1 and digitalRead(solveButton)==HIGH){
    mode++;
    delay(10);
    lcdDisplay.clear();
    lcdDisplay.setCursor(0,2);
    lcdDisplay.print(modes[mode]);
  }
  if (mode==2 and digitalRead(solveButton)==LOW){
    mode++;
    solveStart=millis();
    allOff();
    lcdDisplay.clear();
    digitalWrite(solveLED,HIGH);
    lcdDisplay.setCursor(0,2);
    lcdDisplay.print(modes[mode]);
  }
  if (mode==3 and digitalRead(solveButton)==HIGH){
    mode++;
    solveFinish=millis();
    allOff();
    digitalWrite(doneLED,HIGH);
    lcdDisplay.setCursor(0,2);
    lcdDisplay.print(modes[mode]);
    saveResults();    
  }
  if (mode==4){
    unsigned long blinkTime=(millis()/1000);
    if ((blinkTime/2.00)==int(blinkTime/2.00)){
      digitalWrite(doneLED,HIGH);
    }
    else{
      if (penalty != "F") digitalWrite(doneLED,LOW);
    }
  }
  if (mode==4 and analogRead(coverDetect)<coverThreshold and digitalRead(resetButton)==HIGH){
    mode=0;
    allOff();
    penalty="F";
    digitalWrite(readyLED,HIGH);
    lcdDisplay.setCursor(0,2);
    lcdDisplay.print(modes[mode]);
    lcdDisplay.clear();
    lcdDisplay.setCursor(0,0);
    lcdDisplay.print("Ready");
  }
  if (mode==1 or mode==2){
    displayInspectTime();
    beepTimer=millis()- inspectStart;
    if ((alertOne < beepTimer) && (beepTimer < alertOne + 200)
     || (alertTwo < beepTimer) && (beepTimer < alertTwo + 200)
     || (inspectLimit < beepTimer) && (beepTimer < inspectLimit + 200)
     ){
      digitalWrite(beeper,HIGH);
    }
    else {
      digitalWrite(beeper,LOW);
    }
  }
  if (mode==3){
    displaySolveTime();
  }
  if (mode==0){
    displayCurrentTime();
  }
  

}
