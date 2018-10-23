void setup(){
  pinMode(3,OUTPUT);//数字3设为输出
  pinMode(4,INPUT_PULLUP);//数字4设为输入上拉（无输入时为高电平）
  digitalWrite(3,HIGH);//初始化LED灯为点亮状态
}
void loop(){
  if (digitalRead(4)==LOW)//检测到开关按下
  {
    digitalWrite(3,!digitalRead(3));//改变LED状态
    while (digitalRead(4)==LOW)//等待开关松开
    {delay(10);}
  }
  delay(10);//控制循环频率
}
