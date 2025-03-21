# Currently in production
Below is notes on how the project is going, what we are doing and what to do next.

# Current state
Fungerar.
Går att köra spelet på och går även att lägga till users till databasen.

# Next steps

### Prompt engineering.
- Dice rolls är för svåra. Ibland måste jag rulla 15 för att gå iväg från en nyckel på golvet.
- Den genererade storyn verkar inte alltid ta i hänsyn till om jag lyckades eller ej med min dice roll. 

### Endpoints
- RATE LIMITING FOR GOD SAKE

- /save_game
    Spara player info, inventory och alla scenes (komprimerade).
    Sparar även alla inputs till user-table

- /starting_story
    Hämta en starting story från databasen.

- /load_game
    Ladda en session från databasen.

- /login
    Logga in eller skapa nytt konto.

- /update_user
    Uppdatera användarinfo.

- /logout
    Logga ut.

- /reset_password