

#include "I2Cdev.h"

#include "MPU6050_6Axis_MotionApps20.h"

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

// I2C (default 0x68)
MPU6050 mpu;

#define OUTPUT_READABLE_YAWPITCHROLL


#define INTERRUPT_PIN 2  


// MPU control/status vars

bool dmpReady = false;  
uint8_t mpuIntStatus;   
uint8_t devStatus;      
uint16_t packetSize;    
uint16_t fifoCount;     
uint8_t fifoBuffer[64]; 

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector



// ================================================================
// ===                      MICRO                    ===
// ================================================================
const uint8_t MIC_D = 3;          // digital
const int pinEntrada = 3;

int contadorEntradas = 0;
unsigned long tiempoInicio = 0;
unsigned long ultimaEntrada = 0;

const unsigned long ventana = 2000;       // 1 seg
const unsigned long debounce = 100;        
bool ventanaActiva = false;

String texto = "non";

// ================================================================
// ===                      INITIAL SETUP                       ===
// ================================================================

void setup() {
   
    pinMode(pinEntrada, INPUT);
   
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
        Wire.setClock(100000);    //   (cambiado a 100 KHz)  400kHz I2C clock. Comment this line if having compilation difficulties
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif

   
    Serial.begin(115200);

    // initialize device
    Serial.println(F("Initializing I2C devices..."));
    mpu.initialize();
    pinMode(INTERRUPT_PIN, INPUT);

    // verify connection
    Serial.println(F("Testing device connections..."));
    Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));


    // load and configure the DMP
    Serial.println(F("Initializing DMP..."));
    devStatus = mpu.dmpInitialize();

    // supply your own gyro offsets here, scaled for min sensitivity
    mpu.setXGyroOffset(-46);
    mpu.setYGyroOffset(42);
    mpu.setZGyroOffset(102);
    mpu.setZAccelOffset(1239); // 1688 factory default for my test chip

    
    if (devStatus == 0) {
       
        mpu.CalibrateAccel(6);
        mpu.CalibrateGyro(6);
        mpu.PrintActiveOffsets();
        
        Serial.println(F("Enabling DMP..."));
        mpu.setDMPEnabled(true);

     
        Serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
        Serial.print(digitalPinToInterrupt(INTERRUPT_PIN));
        Serial.println(F(")..."));
        
        mpuIntStatus = mpu.getIntStatus();

       
        Serial.println(F("DMP ready! Waiting for first interrupt..."));
        dmpReady = true;

      
        packetSize = mpu.dmpGetFIFOPacketSize();
    } else {

        Serial.print(F("DMP Initialization failed (code "));
        Serial.print(devStatus);
        Serial.println(F(")"));
    }

}



// ================================================================
// ===                    MAIN PROGRAM LOOP                     ===
// ================================================================

void loop() {



// ================================================================
// ===                    MICRO                    ===
// ================================================================
//int estado = digitalRead(MIC_D);



int estado = digitalRead(pinEntrada);
  static int ultimoEstado = LOW;

 -
  if (estado == HIGH && ultimoEstado == LOW) {

    unsigned long ahora = millis();


    if (ahora - ultimaEntrada > debounce) {

      ultimaEntrada = ahora;  

      if (!ventanaActiva) {
        ventanaActiva = true;
        tiempoInicio = ahora;
        contadorEntradas = 0;
      }

      contadorEntradas++;
    }
  }
  ultimoEstado = estado;


  // --- Procesar ventana de 1 segundo ---
  if (ventanaActiva && millis() - tiempoInicio >= ventana) {

    if (contadorEntradas == 1) {
      texto = "clic";
      //Serial.println("clic");

    }
    else if (contadorEntradas >= 2) {
      //Serial.println("anticlic");
      texto = "anticlic";

    }

    ventanaActiva = false;
    contadorEntradas = 0;
  }
// ================================================================



    if (!dmpReady) return;

    if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) { // Get the Latest packet 
        //YPR (Z,Y,X) + Aceleracion
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
        Serial.print(ypr[0] * 180/M_PI);
        Serial.print(",");
        Serial.print(ypr[1] * 180/M_PI);
        Serial.print(",");
        Serial.print(ypr[2] * 180/M_PI);
        Serial.print(",");
        //acc
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetAccel(&aa, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
        mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
        Serial.print(aaWorld.x);
        Serial.print(",");
        Serial.print(aaWorld.y);
        Serial.print(",");
        Serial.print(aaWorld.z);

        if (texto != "non"){
          Serial.print(",");
          Serial.println(texto);
          texto ="non";
        } else {
          Serial.print(",");
          Serial.println(texto);

        }


        /*
  
        // display initial world-frame acceleration, adjusted to remove gravity
        // and rotated based on known orientation from quaternion
        mpu.dmpGetQuaternion(&q, fifoBuffer);
        mpu.dmpGetAccel(&aa, fifoBuffer);
        mpu.dmpGetGravity(&gravity, &q);
        mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);
        mpu.dmpGetLinearAccelInWorld(&aaWorld, &aaReal, &q);
        Serial.print("aworld\t");
        Serial.print(aaWorld.x);
        Serial.print("\t");
        Serial.print(aaWorld.y);
        Serial.print("\t");
        Serial.println(aaWorld.z);*/
        
        
    }
}
