Refactor done.
Kör main.py i root för att starta servern.

# Current state
Backend fungerar som den ska.
Alla api calls funkar. Inga oväntade bugs när jag använder frontend.

# Next steps
### Prompt engineering.
- Dice rolls är för svåra. Ibland måste jag rulla 15 för att gå iväg från en nyckel på golvet.
- Den genererade storyn verkar inte alltid ta i hänsyn till om jag lyckades eller ej med min dice roll. 

### Databas
- Skapa databasen, tabeller, data
- Connection pool
- Implementera fetch story funktionalitet
- Implementera save funktionalitet
- Implementera users

### Endpoints
- /save_game
    Spara player info, inventory och alla scenes (komprimerade).

- /load_game
    Ladda en session från databasen.

- /login
    Logga in eller skapa nytt konto.

