Det är nog dags att pusha detta till main snart

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

### Backend code
- Splice context med limit på 10 stories.
    - Lägg spliceade stories i en lista som vi postar till db när session tar slut.
- Validering av music/path-output från LLM API.
    - Vi kan kanske koppla ett schema till detta med två fält, literal[]
    - Vi kan även använda difflib för att ersätta close matches
    - Vi validerar redan att kategori och subkategori matchar i prompt_builder/_validate_mood_prompt.
