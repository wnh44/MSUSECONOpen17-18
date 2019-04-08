#include <motorController.h>
#include <AllSensors.h>
#include <Servo.h> 

// Conveyorbelt and encoder setup
#include <Wire.h>
#include <Adafruit_MotorShield.h>
Adafruit_MotorShield conveyorMotorShield = Adafruit_MotorShield(0x60); //Sheild address
Adafruit_DCMotor *conveyorMotor = conveyorMotorShield.getMotor(2); // DC motor on M2


Servo myservo1;  // create servo object to control a servo flag
Servo myservo2;
int pos = 0;  //setting initial variables. Had a bug where these have to be declared below setup() (????)
int c_pos = 0;


bool motorRunning = false;
bool stalled = false;
int stallDelay = 5; // Mutliples of 10 ms to delay before reacting
int pause = 100; // ms to wait before changing motor direction
int interruptPin = 2; // Can only be 2 or 3


AllSensors *sensors;
motorController *motors;

String currentMessage;


//Gets a whole word from command ---------------------------------------

// Parses a given word from the given string
String getXword(int wordNum, String command, String delimiter){
  int currentPlace = 0; // The first index of the current word we are reading
  int currentWord = 0;  // The index of the current word we are reading

  // Loops through and gets each word between the delimiter
  for (int i = 0; i < command.length(); i++){
    // If it hits a delimiter, return the word if its the number word we want
      // Or increment our word counters and keep searching
    if (command.substring(i,i+1) == delimiter){
      if (currentWord == wordNum){
        return command.substring(currentPlace, i);
      }else {
        currentPlace = i+1;
        currentWord++;
      }
    }
    
    // Returns the word if it is the last word and doesn't have a space after
    if (i == (command.length()-1) && (currentWord) == wordNum){
      return command.substring(currentPlace, i+1);
    }
  }

  // Returns blank if the word isn't found
  return "BLANK";
}


// Parses and executes commands -----------------------------------------

void parseCommand(String command){
  String firstWord = getXword(0, command, " ");

  // All the get commands for reading sensors
  if (firstWord == "GET"){
    String secondWord = getXword(1, command, " ");
    if (secondWord == "ultrasonic"){
       float ultrasonic_reading = sensors->scanUltraSonic2();
       Serial.print("Getting ultrasonic reading: ");
       Serial.println(ultrasonic_reading);
    }

    else if (secondWord == "color"){
       String color_reading = sensors->getHexColor();
       Serial.print("Getting color reading: ");
       Serial.println(color_reading);
    }

    else if (secondWord == "lidar"){
      float lidar_reading = sensors->scanliDAR1();
      Serial.print("Getting lidar1 reading: ");
      Serial.println(lidar_reading);
    }

    else{
      Serial.println("Did not issue correct GET command");
    }

    // All the commands for controlling motors
  } else if (firstWord == "GO"){
    String secondWord = getXword(1, command, " ");

    if (secondWord == "forward") {
      // NEED TO FIX PARSING OF INTS, NOT WORKING??????
      String motor_speed_string = getXword(2, command, " ");
      int motor_speed = motor_speed_string.toInt();
      Serial.println("Going forward at speed " + motor_speed_string);
      motors->goForward(motor_speed);
    }else if (secondWord == "backward") {
      String motor_speed_string = getXword(2, command, " ");
      int motor_speed = motor_speed_string.toInt();
      Serial.println("Going backward at speed " + motor_speed_string);
      motors->goBackward(motor_speed);
    }else if (secondWord == "stop") {
      Serial.println("Stopping");
      motors->stop();
    }else if (secondWord == "right") {
      String motor_speed_string = getXword(2, command, " ");
      int motor_speed = motor_speed_string.toInt();
      Serial.println("Going right at speed " + motor_speed_string);
      motors->turnRight(twist, motor_speed);
    }else if (secondWord == "left") {
      String motor_speed_string = getXword(2, command, " ");
      int motor_speed = motor_speed_string.toInt();
      Serial.println("Going left at speed " + motor_speed_string);
      motors->turnLeft(twist, motor_speed);
    }else {
      Serial.println("Incorrect GO command");
    }
  } else if (firstWord == "conveyor"){
    String secondWord = getXword(1, command, " ");

    if (secondWord == "start") {
      startMotor(200);
      Serial.println("Starting conveyor motor");
    } else if (secondWord == "stop"){
      releaseMotor();
      Serial.println("Stopping conveyor motor");
    }
  } else if (firstWord == "flag"){
    String secondWord = getXword(1, command, " ");

    if (secondWord == "up"){
      Serial.println("Sending up flag to 140 degrees");
      gotopos(140);
    } else if (secondWord == "down"){
      Serial.println("Sending down flag to 70 degrees");
      gotopos(70);
    }
  }
  
  else{
    Serial.println("Parsed: " + getXword(1, command, " "));
  }
  return;
}


// Conveyor Motor setup ------------------------------------------

void releaseMotor()
{
    // Serial.println("Stopping");
    stalled = false;
    motorRunning = false;
    // Ensure timers are on
    // Stop motor
    conveyorMotor->setSpeed(0);
    delay( pause );
    
    // Run backwards
    conveyorMotor->run(BACKWARD);
    conveyorMotor->setSpeed(255);
    // Let run for some time
    for (int i = 0; i < 5; i++)
      delay( pause );
    // Stop motor
    conveyorMotor-> setSpeed(0);
    conveyorMotor->run(RELEASE);
    // Clear stall flags
    
}
void startMotor(int speed)
{
    // Serial.println("Starting");
    // Set stall flags
    motorRunning = true;
    stalled = false;
    // Start interupts again
    conveyorMotor->run(FORWARD);
    conveyorMotor->setSpeed( speed );
}

void gotopos(int pos){
   if(c_pos < pos){
     //for loop to gradually change pos. For some reason, the servo fails to move when just given a large position.
     for(c_pos; c_pos < pos; c_pos++){ 
      myservo1.write(c_pos);              // tell servo to go to the new current position.
      myservo2.write(c_pos);
      delay(15);                       // waits 15ms for the servo to reach the position. This can be changed to change the rate of speed the servo moves. 
     } 
   }
   else{
        for(c_pos; c_pos > pos; c_pos--) // goes from 0 degrees to 180 degrees 
     {                                  // in steps of 1 degree 
      myservo1.write(c_pos);              // tell servo to go to position in variable 'pos' 
      myservo2.write(c_pos);
      delay(15);                       // waits 15ms for the servo to reach the position 
     }
   }
} 







void setup() {
  Serial.begin(9600);
  sensors = &AllSensors(true, true, 10, 11, 0, 0, false);
  motors = &motorController(0x60, 2);

  
  conveyorMotorShield.begin();
//  setupInterrupts();
  
  // Weird glitch, wont turn later on if dont do this to activate motors???
  motors->turnRight(twist, 100);
  delay(1);
  motors->turnLeft(twist, 100);
  delay(1);
  motors->stop();

  myservo1.attach(9);  // attaches the servo on pin 9 to the servo object 
  myservo1.write(0);
  myservo2.attach(10);  // attaches the servo on pin 10 to the servo object 
  myservo2.write(0);
}

void loop() {
  while(Serial.available()){
    char t = Serial.read();
    if (t == '@'){
      parseCommand(currentMessage);
      currentMessage = "";
    }
    else if (t != ""){
      currentMessage.concat(t);
    }
  }

  if (stalled == true){
        releaseMotor();
  }
  
}
