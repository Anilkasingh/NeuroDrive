#include <Arduino.h>
#include <SoftwareSerial.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <PubSubClient.h>

const char* ssid = "EACCESS-M2";
const char* password = "hostelnet";

const char* mqtt_host = "172.16.38.144"; 
const int   mqtt_port = 1883;
const char* mqtt_user = "guest";
const char* mqtt_pass = "guest";

WiFiUDP udp;
SoftwareSerial ard(14, 12);   // RX, TX from Arduino
NTPClient timeClient(udp, "pool.ntp.org", 19800, 60000);

WiFiClient espClient;
PubSubClient mqtt(espClient);

String data = "";
unsigned int samples = 0;

void connectMQTT() {
  while (!mqtt.connected()) {
    Serial.print("Connecting to MQTT... ");
    if (mqtt.connect("esp8266-client", mqtt_user, mqtt_pass)) {
      Serial.println("Connected!");
    } else {
      Serial.print("Failed. rc=");
      Serial.println(mqtt.state());
      delay(2000);
    }
  }
  mqtt.setBufferSize(4096);
}

void setup() {
  Serial.begin(115200);
  ard.begin(9600);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected!");

  mqtt.setServer(mqtt_host, mqtt_port);

  connectMQTT();

  timeClient.begin();
}

void loop() {
  mqtt.loop();  // keep MQTT alive

  if (!mqtt.connected()) {
    connectMQTT();
  }

  if (ard.available()) {
    String line = ard.readStringUntil('\n');
    line.trim();

    if (samples > 0) data += ",";
    data += line;
    samples++;

    if (samples == 50) {
      timeClient.update();
      String timestamp = timeClient.getFormattedTime();

      String payload = data + ";" + timestamp;

      Serial.println("Publishing 500 samples:");
      Serial.println(payload);

bool ok = mqtt.publish("raw", payload.c_str());

if (!ok) {
  Serial.println("MQTT PUBLISH FAILED!");
} else {
  Serial.println("MQTT PUBLISH SUCCESS");
}
      samples = 0;
      data = "";
    }
  }
}
