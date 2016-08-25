#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <Wire.h>  // Include Wire if you're using I2C
#include <ER_MicroOLED.h>  // Include the SFE_MicroOLED library
#define PIN_RESET 255  //
#define DC_JUMPER 0  // I2C Addres: 0 - 0x3C, 1 - 0x3D

// put blynk api code, pushbullet api code and wifi credentials of mobile ap in
char auth[] = "";
char ssid[] = "";
char pass[] = "";
const char* PushBulletAPIKEY = ""; //get it from your pushbullet account
#define buttonPin D7
//////////////////////////////////
MicroOLED oled(PIN_RESET, DC_JUMPER);  // I2C Example
int pokemon_id;
int till_hour;
int till_minute;
int till_second;
String gmaps_string;
unsigned long update_time = millis();
unsigned long till_update_time = millis();
  
String raw_time_string;
int date_hour;
int date_second;
int date_minute;
String minutes_string;
String seconds_string;
long till_second_sum;
long date_second_sum;

unsigned long variable_update_time = millis(); 
unsigned long block_update_time = millis();
int old_till_hour;
int old_till_minute;
int old_till_second;
int old_pokemon_id;
float old_lat;
float old_lng;
int lat[5];
int lng[5];
String string_lat[5];
String string_lng[5];
bool stop_net = false;
bool button_possible = false;

String pkmn[]{
        "Keins",
        "Bisasam",
        "Bisaknosp",
        "Bisaflor",
        "Glumanda",
        "Glutexo",
        "Glurak",
        "Schiggy",
        "Schillok",
        "Turtok",
        "Raupy",
        "Safcon",
        "Smettbo",
        "Hornliu",
        "Kokuna",
        "Bibor",
        "Taubsi",
        "Tauboga",
        "Tauboss",
        "Rattfratz",
        "Rattikarl",
        "Habitak",
        "Ibitak",
        "Rettan",
        "Arbok",
        "Pikachu",
        "Raichu",
        "Sandan",
        "Sandamer",
        "Nidoran♀",
        "Nidorina",
        "Nidoqueen",
        "Nidoran♂",
        "Nidorino",
        "Nidoking",
        "Piepi",
        "Pixi",
        "Vulpix",
        "Vulnona",
        "Pummeluff",
        "Knuddeluff",
        "Zubat",
        "Golbat",
        "Myrapla",
        "Duflor",
        "Giflor",
        "Paras",
        "Parasek",
        "Bluzuk",
        "Omot",
        "Digda",
        "Digdri",
        "Mauzi",
        "Snobilikat",
        "Enton",
        "Entoron",
        "Menki",
        "Rasaff",
        "Fukano",
        "Arkani",
        "Quapsel",
        "Quaputzi",
        "Quappo",
        "Abra",
        "Kadabra",
        "Simsala",
        "Machollo",
        "Maschock",
        "Machomei",
        "Knofensa",
        "Ultrigaria",
        "Sarzenia",
        "Tentacha",
        "Tentoxa",
        "Kleinstein",
        "Georok",
        "Geowaz",
        "Ponita",
        "Gallopa",
        "Flegmon",
        "Lahmus",
        "Magnetilo",
        "Magneton",
        "Porenta",
        "Dodu",
        "Dodri",
        "Jurob",
        "Jugong",
        "Sleima",
        "Sleimok",
        "Muschas",
        "Austos",
        "Nebulak",
        "Alpollo",
        "Gengar",
        "Onix",
        "Traumato",
        "Hypno",
        "Krabby",
        "Kingler",
        "Voltobal",
        "Lektrobal",
        "Owei",
        "Kokowei",
        "Tragosso",
        "Knogga",
        "Kicklee",
        "Nockchan",
        "Schlurp",
        "Smogon",
        "Smogmog",
        "Rihorn",
        "Rizeros",
        "Chaneira",
        "Tangela",
        "Kangama",
        "Seeper",
        "Seemon",
        "Goldini",
        "Golking",
        "Sterndu",
        "Starmie",
        "Pantimos",
        "Sichlor",
        "Rossana",
        "Elektek",
        "Magmar",
        "Pinsir",
        "Tauros",
        "Karpador",
        "Garados",
        "Lapras",
        "Ditto",
        "Evoli",
        "Aquana",
        "Blitza",
        "Flamara",
        "Porygon",
        "Amonitas",
        "Amoroso",
        "Kabuto",
        "Kabutops",
        "Aerodactyl",
        "Relaxo",
        "Arktos",
        "Zapdos",
        "Lavados",
        "Dratini",
        "Dragonir",
        "Dragoran",
        "Mewtu",
        "Mew",  
};


uint8_t pokeball [] = {
0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x3F, 0x3F, 0x1F, 0x0F, 0x0F, 0x07, 0x03, 0x03,
0x03, 0x01, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x01, 0x03,
0x03, 0x03, 0x07, 0x0F, 0x0F, 0x1F, 0x3F, 0x3F, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
0xFF, 0x5F, 0x17, 0x0F, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x03, 0x0F, 0x17, 0x5F, 0xFF,
0x81, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80,
0x80, 0x80, 0x80, 0x80, 0x80, 0xE0, 0xF0, 0xF8, 0x2C, 0x0E, 0x06, 0x06, 0x03, 0x03, 0x03, 0x03,
0x03, 0x03, 0x03, 0x03, 0x06, 0x06, 0x0E, 0x2C, 0xF8, 0xF0, 0xE0, 0x80, 0x80, 0x80, 0x80, 0x80,
0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x81,
0x80, 0x00, 0x00, 0x00, 0x70, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0,
0xF0, 0xF0, 0xC0, 0x80, 0x01, 0x07, 0x1F, 0x1F, 0x34, 0x70, 0x60, 0x60, 0xC0, 0xC0, 0xC0, 0xC0,
0xC0, 0xC0, 0xC0, 0xC0, 0x60, 0x60, 0x70, 0x34, 0x1F, 0x0F, 0x07, 0x01, 0x80, 0xC0, 0xF0, 0xF0,
0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0x70, 0x00, 0x00, 0x00, 0x80,
0xFF, 0xFA, 0xE8, 0xF0, 0xC0, 0x81, 0x03, 0x07, 0x1F, 0x1F, 0x3F, 0x7F, 0xFF, 0xFF, 0xFF, 0xFF,
0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0xFE, 0xFC, 0xFC, 0xF8, 0xF8, 0xF8, 0xF0, 0xF0, 0xF0, 0xF0,
0xF0, 0xF0, 0xF0, 0xF0, 0xF8, 0xF8, 0xF8, 0xFC, 0xFC, 0xFE, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
0xFF, 0xFF, 0xFF, 0xFF, 0x7F, 0x3F, 0x1F, 0x1F, 0x07, 0x03, 0x81, 0xC0, 0xF0, 0xE8, 0xFA, 0xFF,
0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFE, 0xFC, 0xFC, 0xF8, 0xF0, 0xF0, 0xE0, 0xC1, 0xC3,
0xC3, 0x87, 0x87, 0x07, 0x0F, 0x0F, 0x8F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x3F, 0x3F, 0x3F, 0x3F,
0x3F, 0x3F, 0x3F, 0x3F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x8F, 0x0F, 0x0F, 0x07, 0x87, 0x87, 0xC3,
0xC3, 0xC1, 0xE0, 0xF0, 0xF0, 0xF8, 0xFC, 0xFC, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
};

void setup()
{
  pinMode(buttonPin, INPUT);
  // below caused by my setup of button pin
//  pinMode(D5, OUTPUT);
//  digitalWrite(D5, LOW);
//  pinMode(D6, OUTPUT);
//  digitalWrite(D6, HIGH);
  //////////////////////
  Serial.begin(9600);
  Blynk.begin(auth, ssid, pass);
  oled.begin();
  oled.display();   
  delay(1000);
}

String getTime() {
  WiFiClient client;
  while (!!!client.connect("google.de", 80)) {
    Serial.println("connection failed, retrying...");
  }
  client.print("HEAD / HTTP/1.1\r\n\r\n");
  while (!!!client.available()) {
    yield();
  }
  while (client.available()) {
    if (client.read() == '\n') {
      if (client.read() == 'D') {
        if (client.read() == 'a') {
          if (client.read() == 't') {
            if (client.read() == 'e') {
              if (client.read() == ':') {
                client.read();
                String theDate = client.readStringUntil('\r');
                client.stop();
                return theDate;
              }
            }
          }
        }
      }
    }
  }
}

void update_time_int() {
  if ( (millis() - update_time) >= 5000 && stop_net == false) {
    raw_time_string = getTime();
    Serial.println(raw_time_string);
    date_hour = raw_time_string.substring(17, 19).toInt();
    //////cause utc+2
    date_hour = date_hour + 2;
    date_minute = raw_time_string.substring(20, 22).toInt();
    date_second = raw_time_string.substring(23, 25).toInt();
    update_time = millis();
  }
}

void send_gmap_to_pushbullet(){
  const char* host = "api.pushbullet.com";
  const int httpsPort = 443;
  const char* fingerprint = "2C BC 06 10 0A E0 6E B0 9E 60 E5 96 BA 72 C5 63 93 23 54 B3"; 
  WiFiClientSecure client;
  if (!client.connect(host, httpsPort)) {
    return;
  }
  if (client.verify(fingerprint, host)) {
    Serial.println("certificate matches");
  } else {
    Serial.println("certificate doesn't match");
  }
  String url = "/v2/pushes";
  String messagebody = "{\"type\": \"link\", \"title\": \""+pkmn[pokemon_id]+"\", \"body\": \"Gotta catch'em all\", \"url\": \""+gmaps_string+"\"}\r\n";
  Serial.print("requesting URL: ");
  Serial.println(url);
  client.print(String("POST ") + url + " HTTP/1.1\r\n" +
               "Host: " + host + "\r\n" +
               "Authorization: Bearer " + PushBulletAPIKEY + "\r\n" +
               "Content-Type: application/json\r\n" +
               "Content-Length: " +
               String(messagebody.length()) + "\r\n\r\n");
  client.print(messagebody);


}



BLYNK_WRITE(V0)
{
  pokemon_id = param.asInt();
  block_update_time = millis();
  stop_net = true;
}

BLYNK_WRITE(V1)
{
  lat[1] = param.asInt();
}

BLYNK_WRITE(V2)
{
  lng[1] = param.asInt();
}

BLYNK_WRITE(V3)
{
  lat[2] = param.asInt();
}

BLYNK_WRITE(V4)
{
  lng[2] = param.asInt();
}

BLYNK_WRITE(V5)
{
  lat[3] = param.asInt();
}

BLYNK_WRITE(V6)
{
  lng[3] = param.asInt();
}

BLYNK_WRITE(V7)
{
  lat[4] = param.asInt();
}

BLYNK_WRITE(V8)
{
  lng[4] = param.asInt();
}


BLYNK_WRITE(V9)
{
  // cause utc+2 in summer in germany
  till_hour = param.asInt() + 2;
  Serial.println(till_hour);
}

BLYNK_WRITE(V10)
{
  till_minute = param.asInt();
  Serial.println(till_minute);
}

BLYNK_WRITE(V11)
{
  till_second = param.asInt();
  Serial.println(till_second);
  stop_net = false;
}

void update_till_time(){
  if ( ((millis() - till_update_time) >= 5000 && stop_net == false) &&((till_hour == old_till_hour && till_minute == old_till_minute && till_second == old_till_second && pokemon_id == old_pokemon_id )||(till_hour != old_till_hour && till_minute != old_till_minute && till_second != old_till_second && pokemon_id != old_pokemon_id ))) { 
      till_second_sum = till_second + (till_minute*60) + (till_hour*3600);
      date_second_sum = date_second + (date_minute*60) + (date_hour*3600);
      if (( till_second_sum - date_second_sum <= 0)) {
        button_possible = false;
        oled.clear(PAGE);
        oled.drawBitmap(pokeball);
        oled.display();  
        till_update_time = millis();
        delay(200);
      }
  else {
        button_possible = true;  
        oled.clear(PAGE);
        oled.setFontType(0);
        oled.setTextColor(WHITE);
        oled.setCursor(0, 0);
        oled.print("A wild");
        oled.setCursor(0, 9);
        oled.print(pkmn[pokemon_id]);
        oled.setCursor(1, 18);
        oled.print("catch");
        oled.setCursor(2, 27);
        oled.print("within");
        oled.display();
        delay(100);
        oled.setFontType(0);
        oled.setTextColor(WHITE);
        oled.setCursor(0, 41);
        
        minutes_string = String((till_second_sum - date_second_sum) /60);
        Serial.println("Timer Minutes: "+ minutes_string);
        seconds_string = String((till_second_sum - date_second_sum) % 60);
        Serial.println("Timer Seconds: "+ seconds_string); 
        
        oled.print(minutes_string +":"+seconds_string);
        oled.display();
        till_update_time = millis();
        delay(100);
      }
  }
}


void update_old_variables(){
  if ((millis() - variable_update_time) >= 7000 && stop_net == false){
    old_till_hour = till_hour;
    old_till_minute = till_minute;
    old_till_second = till_second;
    old_pokemon_id = pokemon_id;
    
    // back correcting of removed zeros at beginning of two figure values
    if (lat[2] < 10){
      string_lat[2] = "0"+ String(lat[2]);
    }
    else{
      string_lat[2] = String(lat[2]);
    }

    if (lat[3] < 10){
      string_lat[3] = "0"+ String(lat[3]);
    } 
    else{
      string_lat[3] = String(lat[3]);  
    }

    
    if (lng[2] < 10){
      string_lng[2] = "0"+ String(lng[2]);
    } 
    else{
      string_lng[2] = String(lng[2]);
    }
      
    if (lng[3] < 10){
      string_lng[3] = "0"+ String(lng[3]);
    }  
    else{
      string_lng[3] = String(lng[3]);
    }
    //setup of the gmaps string for sending over pushbullet at button press         
    gmaps_string = "http://maps.google.com/maps?q="+String(lat[1])+"."+string_lat[2]+string_lat[3]+String(lat[4])+","+String(lng[1])+"."+string_lng[2]+string_lng[3]+String(lng[4]);
    Serial.println(gmaps_string);
    variable_update_time = millis();   
  } 
}


void loop()
{
  if (digitalRead(buttonPin) == HIGH && button_possible == true){
    send_gmap_to_pushbullet(); 
  }

  if ((millis() - block_update_time) >= 20000 && stop_net == true) {
    stop_net = false;
    block_update_time = millis();
  }
  Blynk.run();
  update_time_int();
  update_till_time();
  update_old_variables();
  delay(50);
}
