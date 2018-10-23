char inByte;
String temp;
void setup(){
  Serial.begin(9600);//初始化串口
  Serial.println("Hello");//打印字符串并换行
}
void loop(){
  while (Serial.available()>0) //判断串口是否有数据
  {
    inByte = Serial.read();//读取数据，串口一次只能读1个字符
    temp += inByte;//把读到的字符存进临时变量里面缓存，
    //再继续判断串口还有没有数据，直到把所有数据都读取出来
  }
  if (temp!="")//判断是否收到数据
    Serial.println(temp);//打印收到的数据
  temp="";//清空临时变量准备下一次接收
  delay(10);
}
