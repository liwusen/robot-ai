#include<Wire.h>
const int m[5][2]={{0,0},{2,3},{4,5},{6,7},{8,9}};//{a,b}
const short mc[5][2]={{0,0},{A0,A1},{A2,A3},{A4,A5},{A6,A7}};//{FWD,BKD}
const bool rev[5]={false,false,true,false,true};
bool lasts[5]={true};
long spinCnts[5]={0};
long spinLast[5]={0};
float speed[5]={0};
long lastRunTime=0;
String comdata="";
void(* resetFunc) (void) = 0;//Reset Func
void setup() {
  for(int i=2;i<=9;i++){
    pinMode(i,INPUT_PULLUP);
  }
  for(int i=1;i<=4;i++){
    pinMode(mc[i][0],OUTPUT);
    pinMode(mc[i][1],OUTPUT);
  }
  pinMode(A0,INPUT);
  Serial.begin(9600);
  Serial.println("START");
  analogWrite(A6,128);
}
void serialEvent()
{
  comdata = "";
  char c=Serial.read();
  /*
  if(c=='S'){
    for(int i=0;i<=4;i++){
      int tmp=Serial.parseInt();
      if(tmp>0){
        analogWrite(mc[i][0],tmp);
      }else if(tmp<0){
        analogWrite(mc[i][1],tmp);
      }else{
        analogWrite(mc[i][0],0);
        analogWrite(mc[i][1],0);
      }
      Serial.println(tmp);
    }
  }*/
  if(c=='R'){
    print();
  }
  if(c=='!'){
    resetFunc();
  }
  while (Serial.read() >= 0) {Serial.read();}
}
void print(){
  // for(int i=1;i<=4;i++){
  //   Serial.print(spinCnts[i]);
  //   Serial.print(",");
  // }
  // Serial.println("");
  for(int i=1;i<=4;i++){
    Serial.print(speed[i]);
    Serial.print(",");
  }
  Serial.print(float (analogRead(A0)));
  Serial.println("");
}
void calc(){
  for(int i=1;i<=4;i++){
    speed[i]=(float (spinCnts[i]-spinLast[i]))*20/140;
    if(rev[i]){
      speed[i]=(-speed[i]);
    }
  }
}
void sync(){
  for(int i=1;i<=4;i++){
    spinLast[i]=spinCnts[i];
  }
}
void loop() {
  // A=3 B=2
  //BABA
  /*
  if(digitalRead(A1) && last==false){
    if(!digitalRead(B1)){
      spin_c+=1;
    }else{
      if(digitalRead(B1)){
        spin_c-=1;
      }
    }
    Serial.println(spin_c);
  }
  last=digitalRead(A1);*/
  for(int i=1;i<=4;i++){
    int A=m[i][0],B=m[i][1];
    if(digitalRead(A)&&lasts[i]==false){
      if(!digitalRead(B)){
        spinCnts[i]++;
      }else{
        spinCnts[i]--;
      }
    }
    lasts[i]=digitalRead(A);
  }
  if(millis()-lastRunTime>=50){
    calc();
    sync();
    print();
    lastRunTime=millis();
  }
  return;  
}
