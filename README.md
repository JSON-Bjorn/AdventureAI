# How to run
```bash
git clone https://github.com/JSON-Bjorn/AdventureAI
cd AdventureAI
python-3.13 -m venv venv
source venv/scripts/activate
pip install -r src/requirements/requirements.txt
python run_server.py
```

# IMPORTANT STUFF DURING MIGRATION AND SEPARATION
Vi har hitills kört python version 3.10 eftersom det krockade mellan 3.13 och torch i stable diffusion genereringen.
Hela projektet var baserat på 3.10. Nu har jag fifflat runt lite och lyskas få denna error när jag kör servern:
```bash
  File "C:\Users\Felix\Desktop\Code\Egna projekt\AdventureAI - Full project\backend\src\adventureai.py", line 28, in <module>
    from agents import (
    ...<4 lines>...
    )
ModuleNotFoundError: No module named 'agents'
```
Jag ser detta som ett bra tecken och kommer därför att påstå att vi nu kan köra 3.13 i detta repo!

Se till att avinstallera ditt gamla venv och skapa ett nytt.


# Allmän info om denna branch
Den här branchen är tänkt för att fungera för att kunna konvertera spelet till en webbapplikation där vi kommer fokusera på att använda react för frontend och FastAPI för backend. Vi kommer även hosta det på AWS ihop med en vectordatabas för sessionkontroll samt möjligtvis införa någon form av payment gateway. För tillfället kommer vi detta vara våran huvudbranch där vi pushar upp och förändrar saker över tid.

Troligtvis kommer vi slänga tillbaka denna på main (? mvh felix) eftersom vi inte längre har en webbapp här

# Current state
Vi har en solid plan:
Separera projektet i 4 delar:
- Backend (this)
- [Frontend React app](https://github.com/FelixSoderstrom/adventureai-frontend)
- [StableDiffusion API](https://github.com/FelixSoderstrom/stablediffusion-api)
- [Mistral API](https://github.com/FelixSoderstrom/mistral-api)

Vi kommer basically köra den här servern, ta input från frontend, göra requests till mistral och sd api.
Det slimmar ner detta repo rejält och har bättre separation of concerns.

Sist jag kollade så funkade game loop (innan separering av front och back) och vi kunde få ut text till front end.
Vi fick inget ljud eller bild men bilder genererades och sparades lokalt. Ljudet valdes korrekt.



# Webpage
TBD

# Ongoing Tasks

- Björn:
Just nu håller Björn på med att få Mistral att funka lokalt.
Planen är att köra 7B versionen på hans dator och använda den koden som et skal för den fetarre modellen som kommer köras i cloud.
Vi vill försöka debugga så gott det går innan vi deployar koden på AWS (kommer ta lång tid att debugga, pusha, deploya för varje code change.)
Kanske finns något bättre sätt att göra detta men just nu fokuserar vi på den lilla modellen lokalt.

- Felix:
Felix separerar just nu repon.
Frontend funkar bra.
Servern funkaratt köra. Vi kör fast på imports. Måste koppla bort api, sd och testa igen med en dummy page (se nedan)
Just nu kör backend fortfarande llm api calls till open ai och st generering i samma repo.
Dessa två sistnämnda ska separeras så fort vi vet att allting fungerar som det ska.
Vi måste även lösa problem med att saker inte når vår front end ordentligt innan vi separerar mer på sakerna.

Note to self:
Ta bort alla referenser till openai och stable diffusion i game loopen.
Ersätt dem med placeholder files som hämtar bild, ljud och text lokalt bara för att se om vi kan få grejerna att dyka upp i frontend.
Sedan kopplar vi på en funktion som använder vår api när vi vet att den funkar.

# Completed Tasks
- Tog bort renderingen i pygame och översatte det till react.
- Basic design av react frontend.
- Separering av front, backend.
- Skissat i miro och planerat arbetet framåt.
