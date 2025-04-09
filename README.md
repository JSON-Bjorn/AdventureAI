<<<<<<< HEAD
# Currently in production

Below is notes on how the project is going, what we are doing and what to do next.
=======
# Allmän info om denna branch
Den här branchen är tänkt för att fungera för att kunna köra spelet lokalt. För tillfället kommer vi inte göra några större ändringar i denna branch.

# Setup
- Se till att köra start.bat för att installera alla nödvändiga paket.

- Kör adventureai.py för att starta applikationen
>>>>>>> 35a3ecb07d66e50cac44980f21107ff46cfb5c1f

# Current state

Pretty big update - Rate Limiting

- Har nu implementerat rate limiting
  Vi använder det som en decorator på vår endpoint.
  Decoratorn tar två argument; authenticated_limit och unauthenticated_limit.
  For now så är dessa satta på samma värde. Vi får prata ihop oss om vad en bra limit kan vara.
  Jag inser nu när jag skriver att jag kanske är snål med upper limit.

Det enda vi behöver tänka på är att använda decoratorn under requires_auth-decoratorn.

<<<<<<< HEAD
### How the rate limiter works

- När en endpoint blir requested av en användare:
  - @requires_auth hämtar ut token från headern i requesten och gör en check mot databasen för att se om token är giltig.
    Samtidigt så returnerar vi user_id fron token-tabellen.
  - @rate_limit gör en query på rate_limit-tabellen och filtrerar efter user_id/ip_address kolumnerna(depending on logged in or not) och endpoint_path.
    I samband med detta så får vi ut en lista med unix timestamps som representerar tidigare requests av client mot en specifik endpoint.
  - @rate_limit kontrollerar att vi inte gjort för många requests under den senaste minuten.

# Hur vi kör det lokalt
=======
# Installation Guide for Illustrator Agent
>>>>>>> 35a3ecb07d66e50cac44980f21107ff46cfb5c1f

Starta programmet från root katalogen genom att köra kommandot:

<<<<<<< HEAD
```bash
python main.py
```

Detta skapar tabellerna i databasen (se till att du har rätt struktur i din .env fil (se exemplet i .env.example))

```bash
python -m app.api.v1.database.setup.fill_db
```

Detta kommando fyller databasen med dummy data.

### Additional thoughts/fixes

Arguably kanske det vore bättre att (om användaren gör en request med token), joina dessa två ovan queries.
Det skulle dock kräva en omfaktorering som jag helt enkelt inte orkar med just nu. Men vi skulle effectively skära ner våra database queries med 50%..

# Next steps

### Prompt engineering.

- Dice rolls är för svåra. Ibland måste jag rulla 15 för att gå iväg från en nyckel på golvet.
- Den genererade storyn verkar inte alltid ta i hänsyn till om jag lyckades eller ej med min dice roll.

### Endpoints

- RATE LIMITING FOR GOD SAKE

- /reset_password
  Kommer kräva någon slags emailtjänst.
=======
## 2. Environment Setup
Add these lines to your `.env` file (create it if it doesn't exist):
OPENAI_API_KEY="sk-proj-****************"
IMAGE_MODEL="juggernautXL_juggXILightningByRD"
>>>>>>> 35a3ecb07d66e50cac44980f21107ff46cfb5c1f
