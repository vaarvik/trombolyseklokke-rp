# Trombolyseklokke
Dette er klokke/timer som kan brukes under behandling av slag. Målet med klokken er å bistå i prosedyren som gjøres på sykehuset etter en person har fått slag.

Trombolyseklokken er utviklet i Python og er ment til å kjøre på en Rasberry Pi. I den fysiske løsningen skal knapper være festet til Rasberry Pi-en som kan starte, stoppe og oppdatere klokken.

**MERK:** På grunn av at programmet bruker biblioteket RPi.GPIO som kun kan installeres på en Raspberry Pi, vil det ikke være mulig å kjøre programmet på en annen type datamaskin. Et alternativ er å bruke en virtuell maskin (VM) via for eksempel Oracle Virtual Box og installere operativsystemet til Raspberry Pi. Det vil dog ikke være mulig å starte timerne i en VM ettersom programmet krever at det er eksterne knapper koblet til.

## Installasjon
Merk at denne installsjonsguiden ikke tar hensyn til at man har en annen versjon av python installert (som for eksempel python 2). Hvis dette er tilfellet kan det være man må erstatte pip-kommandoen med "python3 -m pip" og "python" med "python3".
1. For å kjøre koden kreves det at man har python3 installert. Vi benyttet oss av python 3.10.4 i utviklingen av denne løsningen. Python3 kan installeres her: https://www.python.org/downloads/
Påse at tkinter og pip blir installert samtidig som python3 blir installert.
![pip og tkinter markert i installasjonen av python3](/installasjonsbilde.png)
2. Klon dette repo-et fra github.
3. Installer pakkene som kreves for å kjøre koden. Dette gjøres ved åpne en terminal inne i mappen til prosjektet og skrive følgende:
```
pip install -r requirements.txt
```
4. Kjør programmet ved å skrive følgende kommando inne i mappen til prosjektet:
```
python trombolyseklokke.py
```

## Konfigurasjoner
Det er mulig å konfigurere stegnavn og mange sekunder et steg i prosedyren skal vare i konfigurasjonsfilen "config.json".

## Hente ut data
Klokken lagrer tidene etter en prosedyre er fullført. Dette lagres i form av json ved hjelp av et bibliotek som heter tinydb. Dataen kan enkelt hentes ut eller slettes i "db.json"-filen som blir generert når man begynner å bruke programmet.

Dataen som blir lagret sier hvilken måned det var da behandlingen ble gjort, hvor lang tid det ble brukt på hvert steg i prosedyren og totaltiden for hele prosedyren. Her er et eksempel på data som kunne vært lagret etter en behandling:
```
{
  "1": {
    "month": 4,
	"sequences": [
	  {"seconds": 23.0, "name": "Blodpr\u00f8ver"},
	  {"seconds": 277.0, "name": "Klinisk unders\u00f8kelse"},
	  {"seconds": 54.0, "name": "CT"},
	  {"seconds": 46.0, "name": "Trombolyse gitt"}
	],
	"totalSeconds": 400.0
  }
}
```
