#include "Display.h"
#include "DHT11.h"
#include <ArduinoJson.h>

const int PIN_LDR = 16;

void setup()
{
  Serial.begin(9600);
  pinMode(PIN_LDR, INPUT);
}

void loop()
{
    float humidity = DHT11.getHumidity();
    float temperature = DHT11.getTemperature();
    
    int sensorValue = analogRead(PIN_LDR);
    float resistance_sensor;
    resistance_sensor=(float)(1023-sensorValue)*10/sensorValue;
    float lux;
    lux = 325 * pow(resistance_sensor, -1.4);

    JsonDocument doc;

    doc["sensor_id"] = "sensor_2";
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["light"] = lux;

    serializeJson(doc, Serial);
    Serial.println();

    if (isnan(humidity) || isnan(temperature)) {
        Display.show("Err ");
    }
    else
    {
        Display.show(humidity);
        delay(2500);
        Display.show(temperature);
        delay(2500);
    }

}
