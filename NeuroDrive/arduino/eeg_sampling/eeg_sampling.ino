#include <SoftwareSerial.h>

#define SAMPLE_RATE 250
#define BAUD_RATE 9600
#define EEG_PIN0 A0
#define EEG_PIN1 A1
#define ECG_PIN A2

SoftwareSerial esp(2, 3);

void setup() {
	// Serial.begin(BAUD_RATE);
  esp.begin(BAUD_RATE);
}

void loop() {
	static unsigned long past = 0;
	unsigned long present = micros();
	unsigned long interval = present - past;
	past = present;

	static long timer = 0;
	timer -= interval;

	if(timer < 0){
		timer += 1000000 / SAMPLE_RATE;
		float eeg0 = analogRead(EEG_PIN0);
    float eeg1 = analogRead(EEG_PIN1);
    float ecg = analogRead(ECG_PIN);

    esp.print(eeg0);
    esp.print('|');
    esp.print(eeg1);
    esp.print('|');
    esp.println(ecg);
	}
}