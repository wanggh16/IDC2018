#define lf 3
#define lb 5
#define rf 9
#define rb 6
#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpiDriver.h>
void L(int s)
{
  if (s>=0) { analogWrite(lf,s);digitalWrite(lb,LOW);}
  else { analogWrite(lb,-s);digitalWrite(lf,LOW);}
}
void R(int s)
{
  if (s>=0) { analogWrite(rf,s);digitalWrite(rb,LOW);}
  else { analogWrite(rb,-s);digitalWrite(rf,LOW);}
}
int i;
String Temp;
void setup()
{
  pinMode(3,OUTPUT);
  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(9,OUTPUT);
  Serial.begin(9600);
  Mirf.spi = &MirfHardwareSpi;
  Mirf.init();
  Mirf.setTADDR((byte *)"clie1");
  Mirf.setRADDR((byte *)"serv1");
  Mirf.payload = 8; // 长度
  Mirf.channel = 3; // 信道
  Mirf.config();
}
void loop()
{
  byte data[Mirf.payload];
  if(!Mirf.isSending() && Mirf.dataReady())//存在数据
  {
    Mirf.getData(data);
    for (i = 0; i < Mirf.payload; i++) //把收到的信息拼起来，到一个串里面
    {
      Temp += char(data[i]);
    }
    Serial.print("Get:");
    Serial.print(Mirf.payload);
    Serial.print(" ");
    Serial.println(Temp);
  }
  switch (uint8_t(Temp[0]))
  {
    case 1:
    {
      L(uint8_t(Temp[1]));
      R(uint8_t(Temp[2]));
      break;
    }
    case 2:
    {
      L(uint8_t(Temp[1]));
      R(-uint8_t(Temp[2]));
      break;
    }
    case 3:
    {
      L(-uint8_t(Temp[1]));
      R(uint8_t(Temp[2]));
      break;
    }
    case 4:
    {
      L(-uint8_t(Temp[1]));
      R(-uint8_t(Temp[2]));
      break;
    }
  }
  Temp="";
  delay(20);
}
