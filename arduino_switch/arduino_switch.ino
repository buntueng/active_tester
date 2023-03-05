unsigned int red_sw = 2;
unsigned int green_sw = 3;
unsigned int blue_sw = 4;

byte red_sw_state = 0xFF;
byte green_sw_state = 0xFF;
byte blue_sw_state = 0xFF;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(red_sw,INPUT_PULLUP);
  pinMode(green_sw,INPUT_PULLUP);
  pinMode(blue_sw,INPUT_PULLUP);
  
}

void loop() {
  red_sw_state = ((red_sw_state<<1) + digitalRead(red_sw))&0xFF;
  green_sw_state = ((green_sw_state<<1) + digitalRead(green_sw))&0xFF;
  blue_sw_state = ((blue_sw_state<<1) + digitalRead(blue_sw))&0xFF;

  if(red_sw_state == 0xF0){Serial.print("R");}
  if(green_sw_state == 0xF0){Serial.print("G");}
  if(blue_sw_state == 0xF0){Serial.print("B");}

}
