/*
*
* To recieve motion commands, the Arduino recieves a desired 
* rotation velocity via one-directional Serial USB. For this
* purpose, one 'normalized' velocity byte (0 - 255) is used, per
* axis, where 0 results in negative maximal velocity, 255 in positive
* maximal velocity and 128 in zero velocity. Each command contains three
* bytes in total, one per axis and with a line break (or any other char)
* in the end. Commands with more or less than three bytes are ignored.
* 
* This serial velocity command can be overwritten by either the
* joystick 
*
* StallGuard etc. cannot be used for small motor velocities:
* https://www.trinamic.com/fileadmin/assets/Products/ICs_Documents/TMC2209_Datasheet_V103.pdf
*/

#include <TMCStepper.h>
#include <AccelStepper.h>

// mechanical constants
#define GEAR_RATIO 200/10 // 200 stepper rotations result in 10 telescope rotations
#define STEPS_PER_REV 200 // 200 steps are required for a full stepper revolution
#define MICROSTEPS 16     // substeps per step
#define MAX_VEL 1         // DEG/s
#define MAX_ACC 0.5       // DEG/s^2

const float steps_per_deg = GEAR_RATIO * MICROSTEPS * (STEPS_PER_REV / 360.0); //steps/DEG, angular distance the telescope moves for one step
// speeds over 1000 steps/s are unreliable


//joystick pins
#define JOYSTICK_HOR A0
#define JOYSTICK_VER A1

// stepper pins
#define MOSI 32  // software Master Out Slave In (MOSI)
#define MISO 26  // software Master In Slave Out (MISO)
#define SCK 30   // software Slave Clock (SCK)

#define EN_AL 34    // altidude enable
#define DIR_AL 22   // altidude direction
#define STEP_AL 24  // altidude step
#define CS_AL 28    // altidude chip select

#define EN_AZ 46    // azimuth enable
#define DIR_AZ 40   // azimuth direction
#define STEP_AZ 42  // azimuth step
#define CS_AZ 44    // azimuth chip select

#define R_SENSE 0.11f
//#define STALL_VALUE 63 //between [-64..63]

// timing
#define SERIAL_TIMEOUT 5000 // ms, after which time Serial velocity promt is set to zero
#define PROMT_UPDATE_TIME 200 //ms, how often new velocity is updated, must leave 'enough' time for frequent stepper updates

/* ------ variables in global scope ------ */
float velocity_prompt[] = { 0, 0 }; // array storing received rel. velocity
float current_velocity[] = { 0, 0 };
unsigned long last_rcv = 0;  // Serial velocity promt timestamp
bool manual_control;
int i = 0;
unsigned long last_vel_update = 0; 

TMC2130Stepper driver_al = TMC2130Stepper(CS_AL, R_SENSE, MOSI, MISO, SCK);
TMC2130Stepper driver_az = TMC2130Stepper(CS_AZ, R_SENSE, MOSI, MISO, SCK);

AccelStepper stepper_al = AccelStepper(stepper_al.DRIVER, STEP_AL, DIR_AL);
AccelStepper stepper_az = AccelStepper(stepper_az.DRIVER, STEP_AZ, DIR_AZ);

/* ------ functions ------ */

void read_serial_velocity() {
  /* flush serial buffer without blocking and store promted relative velocities */
  char rcv;
  int i=0;
  while (Serial.available()) {
    rcv = Serial.read();
    if(i < 2){
      float vel = float(rcv);
      vel = constrain(vel, 0, 255);
      velocity_prompt[i] = (vel - 128) / 128;
      last_rcv = millis();
    }
    i++;
  }
}

void check_serial_velocity_timeout() {
  /* set promted relative velocities to zero if too old */
  if ((millis() - last_rcv) > SERIAL_TIMEOUT) {
    for (int i = 0; i < 2; i++) {
      velocity_prompt[i] = 0;
    }
  }
}

float joystick_velocity(int joystick_pin) {
  /* return a 'relative' velocity in [-1, 1] for given joystick pin */
  float vel = (analogRead(joystick_pin) - 512.0) / 512.0;
  if (abs(vel) < 0.3) {
    vel = 0;
  }
  return vel;
}

/* ------ main body ------ */
void setup() {
  SPI.begin();
  Serial.begin(921600);
  // while (!Serial)
  //   ;
  // Serial.print("Setup...");
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(JOYSTICK_HOR, INPUT);
  pinMode(JOYSTICK_VER, INPUT);
  digitalWrite(LED_BUILTIN, HIGH);

  // driver setup
  pinMode(CS_AL, OUTPUT);
  digitalWrite(CS_AL, HIGH);
  driver_al.begin();           // Initiate pins and registeries
  driver_al.rms_current(600);  // Set stepper current to 600mA. The command is the same as command TMC2130.setCurrent(600, 0.11, 0.5);
  driver_al.en_pwm_mode(1);    // Enable extremely quiet stepping
  driver_al.pwm_autoscale(1);
  driver_al.microsteps(MICROSTEPS);
  digitalWrite(CS_AL, LOW);

  pinMode(CS_AZ, OUTPUT);
  digitalWrite(CS_AZ, HIGH);
  driver_az.begin();
  driver_az.rms_current(600);
  driver_az.en_pwm_mode(1);
  driver_az.pwm_autoscale(1);
  driver_az.microsteps(MICROSTEPS);
  digitalWrite(CS_AZ, LOW);

  // stepper setup
  stepper_al.setMaxSpeed(MAX_VEL * steps_per_deg);
  stepper_al.setAcceleration(MAX_ACC * steps_per_deg);
  stepper_al.setEnablePin(EN_AL);
  stepper_al.setPinsInverted(false, false, true);
  stepper_al.enableOutputs();

  stepper_az.setMaxSpeed(MAX_VEL * steps_per_deg);
  stepper_az.setAcceleration(MAX_ACC * steps_per_deg);
  stepper_az.setEnablePin(EN_AZ);
  stepper_az.setPinsInverted(false, false, true);
  stepper_az.enableOutputs();
  digitalWrite(LED_BUILTIN, LOW);
  Serial.println("Ready");

}



void loop() {
  if((millis() - last_vel_update) > PROMT_UPDATE_TIME){
    last_vel_update = millis();

    read_serial_velocity();
    check_serial_velocity_timeout();

    float vel_al = joystick_velocity(JOYSTICK_HOR);
    float vel_az = joystick_velocity(JOYSTICK_VER);

    if ((abs(vel_al) > 0.3) || (abs(vel_az) > 0.3)) {
      manual_control = true;
      velocity_prompt[0] = 0;
      velocity_prompt[1] = 0;
    } else {
      vel_al = velocity_prompt[0];
      vel_az = velocity_prompt[1];
    }
    
    current_velocity[0] = vel_al;
    current_velocity[1] = vel_az;

    // power saving
    if(abs(current_velocity[0]) < 0.05){
      stepper_al.disableOutputs();
    }else{
      stepper_al.enableOutputs();      
    }
    if(abs(current_velocity[1]) < 0.05){
      stepper_az.disableOutputs();
    }else{
      stepper_az.enableOutputs();
    }


  //   // Serial.print(">");
  //   // Serial.print(velocity_prompt[0]*MAX_VEL);
  //   // Serial.print(" | ");
  //   // Serial.print(velocity_prompt[1]*MAX_VEL);
  //   // Serial.print(" | ");
  //   // Serial.print(vel_al*MAX_VEL);
  //   // Serial.print(" | ");
  //   // Serial.print(vel_az*MAX_VEL);
  //   // Serial.print(" | ");
  //   // Serial.print(manual_control);  
  //   // Serial.println("<");

  //   // delay(500);

    // LED
    uint8_t led_state = manual_control ? HIGH : LOW;
    digitalWrite(LED_BUILTIN, led_state);
    manual_control = false;  
  }



  stepper_al.setSpeed(MAX_VEL * steps_per_deg * current_velocity[0]);
  stepper_az.setSpeed(MAX_VEL * steps_per_deg * current_velocity[1]);
  stepper_al.run();
  stepper_az.run();
}