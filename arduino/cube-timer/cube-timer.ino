#include <SPI.h>
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
unsigned long inspectLimit=15000;
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

void displayCurrentTime(){
  String timeStamp="";
  now=rtc.now();
  timeStamp.concat(now.hour());
  timeStamp.concat(":");
  timeStamp.concat(now.minute());
  timeStamp.concat(":");
  timeStamp.concat(now.second());
  timeStamp.concat(" ");
  timeStamp.concat(now.month());
  timeStamp.concat("/");
  timeStamp.concat(now.day());
  timeStamp.concat("/");
  timeStamp.concat(now.year());
 
  lcdDisplay.setCursor(0,1);
  lcdDisplay.print(timeStamp);
}

void saveResults(){
  //write SD
  //Write serial
  float inspectTime, solveTime;
  String fileData,filePath;
  File scoreFile;
  inspectTime=(solveStart-inspectStart)/1000.0;
  solveTime=(solveFinish-solveStart)/1000.0;
  lcdDisplay.clear();
  lcdDisplay.setCursor(0,0);
  lcdDisplay.print("Inspect: ");
  lcdDisplay.print(inspectTime);
  lcdDisplay.setCursor(0,1);
  lcdDisplay.print("Solve: ");
  lcdDisplay.print(solveTime);
  if (validSD==1)
  {
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
    fileData="Inspect Time, Solve Time, Inspect Start, Solve Start, Solve Finish";
    scoreFile.println(fileData);
    fileData="";
    fileData.concat(inspectTime);
    fileData.concat(",");
    fileData.concat(solveTime);
    fileData.concat(",");
    fileData.concat(inspectStart);
    fileData.concat(",");
    fileData.concat(solveStart);
    fileData.concat(",");
    fileData.concat(solveFinish);
    scoreFile.println(fileData);
    scoreFile.close();
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
  File verFile;

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
  verFile=SD.open("VERIFY.TXT");
  fileData="";
  while (verFile.available())
  {
    inChar=verFile.read();
    fileData.concat(char(inChar));
  }
  if(fileData == "cubetimer\n")
  {
    lcdDisplay.setCursor(0,0);
    lcdDisplay.print("SD Card OK");
    validSD=1;
  }
  else
  {
    lcdDisplay.setCursor(0,0);
    lcdDisplay.print("No valid SD");
  }
  verFile.close();
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
  if (mode==4 and analogRead(coverDetect)<coverThreshold and digitalRead(resetButton)==HIGH){
    mode=0;
    allOff();
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
     || (alertTwo < beepTimer) && (beepTimer < alertTwo + 200)){
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
