#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpiDriver.h>
char inByte;
String temp="";
void setup()
{
  Serial.begin(9600);
  Mirf.spi = &MirfHardwareSpi;
  Mirf.init();
  Mirf.setRADDR((byte *)"zhuog"); // 标记本地名，用于接收
  Mirf.setTADDR((byte *)"kaao1"); // 标记对方的地址
  Mirf.payload = 8; //缓冲窗口大小，这个代表8个字节
  Mirf.channel = 3; // 信道，决定频率是2.4几GHz
  Mirf.config();
}
void loop()
{
  temp="";
  while (Serial.available() > 0) //判断串口是否有数据
  {
    inByte = Serial.read();//读取数据，串口一次只能读1个字符
    temp += inByte;//把读到的字符存进临时变量里面缓存，
  }
  if (temp != "")  //判断临时变量是否为空
  {
    Sends(temp);
    Serial.println(temp);
  }
  delay(20);
}

void Sends(String str)
{
  int lens;
  lens=str.length(); //获取总长度
  char msg[lens];
  int i;
  for (i=0;i<lens;i++) //字符串转化为int类型
  {
    msg[i]= int(str[i]);
  }
  Mirf.send((byte *)&msg);	//发送
  while(Mirf.isSending()){} //确认是否发送完毕
}
