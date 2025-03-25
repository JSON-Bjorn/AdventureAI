# Currently in production
Below is notes on how the project is going, what we are doing and what to do next.

# Current state
Pretty big update - Rate Limiting

- Har nu implementerat rate limiting
Vi använder det som en decorator på vår endpoint.
Decoratorn tar två argument; authenticated_limit och unauthenticated_limit.
For now så är dessa satta på samma värde. Vi får prata ihop oss om vad en bra limit kan vara.
Jag inser nu när jag skriver att jag kanske är snål med upper limit.

Det enda vi behöver tänka på är att använda decoratorn under requires_auth-decoratorn.

### How the rate limiter works
- När en endpoint blir requested av en användare:
    - @requires_auth hämtar ut token från headern i requesten och gör en check mot databasen för att se om token är giltig.
    Samtidigt så returnerar vi user_id fron token-tabellen.
    - @rate_limit gör en query på rate_limit-tabellen och filtrerar efter user_id/ip_address kolumnerna(depending on logged in or not) och endpoint_path.
    I samband med detta så får vi ut en lista med unix timestamps som representerar tidigare requests av client mot en specifik endpoint.
    - @rate_limit kontrollerar att vi inte gjort för många requests under den senaste minuten.


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