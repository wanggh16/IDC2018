int power=0;//灯亮度的变量
char inByte;
String temp;
void setup(){
  pinMode(3,OUTPUT);
  for (int i=0;i<256;i++)//逐渐变亮
  {
    analogWrite(3,i);
    delay(10);
  }
  for (int i=255;i>=0;i--)//逐渐变暗
  {
    analogWrite(3,i);
    delay(10);
  }
  Serial.begin(9600);
  Serial.println("Hello");
}

void loop(){
  while (Serial.available()>0) //判断串口是否有数据
  {
    inByte = Serial.read();//读取数据，串口一次只能读1个字符
    temp += inByte;//把读到的字符存进临时变量里面缓存，
    //再继续判断串口还有没有数据，直到把所有数据都读取出来
  }
  if (temp!="")  //判断临时变量是否为空
  {
    Serial.println(temp);
    power=temp.toInt();//将字符串转化为整数
    if (power>=0 && power<=255)//合法性检查
      analogWrite(3,power);//写入占空比控制灯的亮度
  }
  temp="";
  delay(10);
}
