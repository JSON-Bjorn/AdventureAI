# Currently in production
Below is notes on how the project is going, what we are doing and what to do next.

# Current state
User authentication är snart klar.
Vi kan:
- Registrera nya användare, nya tokens skapas
- Logga in och få tillbaka nytt token
    Varje gång vi loggar in så tas gamla tokens bort.
- Logga ut, ta bort gamla tokens från db


# Next steps

### Prompt engineering.
- Dice rolls är för svåra. Ibland måste jag rulla 15 för att gå iväg från en nyckel på golvet.
- Den genererade storyn verkar inte alltid ta i hänsyn till om jag lyckades eller ej med min dice roll. 

### Endpoints
- RATE LIMITING FOR GOD SAKE

- /update_user
    Uppdatera användarinfo.

- /reset_password
    Kommer kräva någon slags emailtjänst.