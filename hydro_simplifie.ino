#include <OneWire.h>
#include <DallasTemperature.h>

// Pins des relais pour les pompes goutte à goutte
#define relais1 3
#define relais2 4
#define tmpvcc 12
#define ONE_WIRE_BUS 11

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

char buffer[120];

// Paramètres d'arrosage réglables (en millisecondes)
unsigned long tmp_arrosage1 = 300000;       // Durée arrosage pompe 1 (5 min par défaut)
unsigned long tmp_arrosage2 = 300000;       // Durée arrosage pompe 2 (5 min par défaut)
unsigned long tmp_pause1 = 2160000;         // Temps entre arrosages pompe 1 (36 min par défaut)
unsigned long tmp_pause2 = 2160000;         // Temps entre arrosages pompe 2 (36 min par défaut)

// Variables de timing
unsigned long debut_arrosage1 = 0;          // Quand a commencé le dernier arrosage
unsigned long debut_arrosage2 = 0;
unsigned long fin_cycle1 = 0;               // Quand finit le dernier cycle (arrosage + pause)
unsigned long fin_cycle2 = 0;
unsigned long previousmillistemp = 0;

// États des relais
byte etat_relais1 = 0;
byte etat_relais2 = 0;
float previoustemp = 0;

void setup() {
  pinMode(tmpvcc, OUTPUT);
  pinMode(relais1, OUTPUT);
  pinMode(relais2, OUTPUT);
  digitalWrite(relais1, LOW);
  digitalWrite(relais2, LOW);

  Serial.begin(9600);
  sensors.begin();

  // Test initial du capteur de température
  digitalWrite(tmpvcc, HIGH);
  delay(200);
  sensors.requestTemperatures();
  previoustemp = sensors.getTempCByIndex(0);
  digitalWrite(tmpvcc, LOW);
}

void loop() {
  // Traitement des commandes reçues de l'ESP
  // Remplace le bloc Serial.available() par :
if (Serial.available() > 0) {
      int index = 0;
      delay(100);
      int numChar = Serial.available();
      if (numChar > 119) numChar = 119;
      
      while (numChar--) {
        buffer[index++] = Serial.read();
      }
      buffer[index] = '\0';
      
      // Découper par \n et traiter chaque commande
      char* line = strtok(buffer, "\n\r");
      while (line != NULL) {
        if (strlen(line) > 0) {
          processCommand(line);
        }
        line = strtok(NULL, "\n\r");
      }
  }
  // Mise à jour température (toutes les 3 sec)
  if (millis() - previousmillistemp >= 3000) {
    digitalWrite(tmpvcc, HIGH);
    sensors.requestTemperatures();
    previoustemp = sensors.getTempCByIndex(0);
    digitalWrite(tmpvcc, LOW);
    previousmillistemp = millis();
  }

  // Gestion Pompe 1
  if (etat_relais1 == 1) {
    // En arrosage: vérifier si durée atteinte
    if (millis() - debut_arrosage1 >= tmp_arrosage1) {
      etat_relais1 = 0;
      digitalWrite(relais1, LOW);
      fin_cycle1 = millis();  // Marquer la fin du cycle arrosage
    }
  } else {
    // En pause: vérifier si temps de pause atteint
    if (millis() - fin_cycle1 >= tmp_pause1) {
      etat_relais1 = 1;
      digitalWrite(relais1, HIGH);
      debut_arrosage1 = millis();
    }
  }

  // Gestion Pompe 2 (identique à Pompe 1)
  if (etat_relais2 == 1) {
    if (millis() - debut_arrosage2 >= tmp_arrosage2) {
      etat_relais2 = 0;
      digitalWrite(relais2, LOW);
      fin_cycle2 = millis();
    }
  } else {
    if (millis() - fin_cycle2 >= tmp_pause2) {
      etat_relais2 = 1;
      digitalWrite(relais2, HIGH);
      debut_arrosage2 = millis();
    }
  }

  // Envoi des données toutes les secondes
  static unsigned long lastSendTime = 0;
  if (millis() - lastSendTime >= 1000) {
    // Calculer temps restants
    unsigned long tpsRestant1, tpsRestant2;
    
    if (etat_relais1 == 1) {
      // En arrosage: temps restant avant fin arrosage
      tpsRestant1 = (tmp_arrosage1 > (millis() - debut_arrosage1)) ? 
                    (tmp_arrosage1 - (millis() - debut_arrosage1)) / 1000 : 0;
    } else {
      // En pause: temps restant avant prochain arrosage
      tpsRestant1 = (tmp_pause1 > (millis() - fin_cycle1)) ? 
                    (tmp_pause1 - (millis() - fin_cycle1)) / 1000 : 0;
    }

    if (etat_relais2 == 1) {
      tpsRestant2 = (tmp_arrosage2 > (millis() - debut_arrosage2)) ? 
                    (tmp_arrosage2 - (millis() - debut_arrosage2)) / 1000 : 0;
    } else {
      tpsRestant2 = (tmp_pause2 > (millis() - fin_cycle2)) ? 
                    (tmp_pause2 - (millis() - fin_cycle2)) / 1000 : 0;
    }

    // Envoi: etat1 etat2 tpsRestant1 tpsRestant2 temp(centièmes)
    Serial.print("DATA:");  // ← préfixe unique
    Serial.print(etat_relais1);
    Serial.print(" ");
    Serial.print(etat_relais2);
    Serial.print(" ");
    Serial.print(tpsRestant1);
    Serial.print(" ");
    Serial.print(tpsRestant2);
    Serial.print(" ");
    Serial.println(int(previoustemp * 100));

    lastSendTime = millis();
  }
}

void processCommand(char* cmd) {
  // DEBUG
  //Serial.print("CMD recu: [");
  //Serial.print(cmd);
  //Serial.println("]");

  if (cmd[0] == 'P' || cmd[0] == 'p') {
    int val = atoi(&cmd[1]);
    Serial.print("Pompe1 val: ");
    Serial.println(val);  // DEBUG
    if (val == 1) {
      etat_relais1 = 1;
      digitalWrite(relais1, HIGH);
      debut_arrosage1 = millis();
      //Serial.println("Pompe1 ON!");  // DEBUG
    } else if (val == 0) {
      etat_relais1 = 0;
      digitalWrite(relais1, LOW);
      fin_cycle1 = millis();
      //Serial.println("Pompe1 OFF!");  // DEBUG
    }
  }
  else if (cmd[0] == 'O' || cmd[0] == 'o') {
    int val = atoi(&cmd[1]);
    if (val == 1) {
      etat_relais2 = 1;
      digitalWrite(relais2, HIGH);
      debut_arrosage2 = millis();
     // Serial.println("Pompe2 ON!");  // DEBUG
    }else if (val == 0) {   // ← est-ce que ce bloc existe bien ?
    etat_relais2 = 0;
    digitalWrite(relais2, LOW);
    fin_cycle2 = millis();
  }
  }
  else if (cmd[0] == 'A' || cmd[0] == 'a') {
    char* sep = strchr(cmd, ':');
    if (sep) {
      unsigned long newArrosage = atol(&cmd[2]);
      unsigned long newPause = atol(&sep[1]);
      // Ne reset QUE si valeurs différentes
      if (newArrosage != tmp_arrosage1 || newPause != tmp_pause1) {
        tmp_arrosage1 = newArrosage;
        tmp_pause1 = newPause;
        if (etat_relais1 == 0) fin_cycle1 = millis();
      }
    }
  }
  else if (cmd[0] == 'B' || cmd[0] == 'b') {
    char* sep = strchr(cmd, ':');
    if (sep) {
      unsigned long newArrosage = atol(&cmd[2]);
      unsigned long newPause = atol(&sep[1]);
      if (newArrosage != tmp_arrosage2 || newPause != tmp_pause2) {
        tmp_arrosage2 = newArrosage;
        tmp_pause2 = newPause;
        if (etat_relais2 == 0) fin_cycle2 = millis();
      }
    }
  }
}
