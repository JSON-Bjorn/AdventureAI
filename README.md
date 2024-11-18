# Allmän info om denna branch
School branchen är en nedskalad beta version av vår ambition för det färdiga projektet.
Det fick bli så på grund av deadlines med databas-kursen.
Det kommer dock att funka som en väldigt bra start för projektet i sin helhet och vi kommer självklart att fortsätta arbeta på detta efter att uppgiften är inlämnad (om vi nu FÅR lämna in detta som uppgift, annars är vi cooked!).

Jag har clearat den här filen för school-branchen så att vi kan använda oss av den för att kommunicera vad vi gjort för varje push (om vi vill) tillsammans med lite basic info som kan vara användbar för oss att ha som cheat sheet istället för att gräva i dokumentation och discord DMs.

# Setup
- Se till att köra pip install requirements i ett venv med python version 3.10.
Det var i alla fall 3.10 som gällde för att köra LLM lokkalt (?) eller var det TTS paketet?

- Kör adventureai.py för att starta applikationen

# Current state
Just nu så är programmet inte funktionellt.
Jag håller på att emigrera funktionaliteten i text agent.
Tanken är att varje klass ska vara minimal.
I alla agenter (förutom triage) ska vi bara ha agentens instruktioner eventuellt ett gäng instansvariabler.
Tanken var att text agent skulle hålla 'player_name', 'previous_story' osv och sammanställa det i en sträng som en enda input till agenten.
Detta hade jag tydligen gjort i Triage vilket kanske är att föredra (enbart för att det redan är gjort).

Utöver detta så ska jag börja titta på sound agent, specifikt the narrator.
Det verkade sist när vi pratade som att vi skulle använda oss av swarm exklusivt.
Detta behöver så klart inte vara OpenAI, men de har allt vi behöver (och jag har tokens där som brinner inne annars).
Jag är öppen för att köra saker lokalt men kommer så klart att prioritera användar-upplevelsen med långa loading screens osv.
Säga vad man vill, OpenAI har lite mer GPU än vad vi har..

Vi pratade även om det rent juridiska kring detta projekt.
Vi vill verkligen inte censurera en fiktiv berättelse i ett datorspel.
Men om vi ska hålla data från en användare, särskilt i bildformat, som innehåller olagligt innehåll så är det troligtvis vi som blir ansvariga.
Vi bör titta vidare på användarvillkor, ha ett system som upptäcker olaglig content och flaggar den, vi bör definitivt ha ett sätt som tar bort denna content direkt.
En ganska enkel men väldigt tråkig (och kostsam) lösning på detta är att använda OpenAI exklusivt eftersom modellerna vägrar generera olaglig content.

Vi kan diskutera huruvida AI genererat material kan vara olagligt eller om det bara defineras som konst.
Jag vet till exempel inte hur det skulle se ut juridiskt om jag ställde mig med en pensel och målade en tavla varje gång användaren ber om det.
Skulle det vara olagligt? Är det olagligt om jag säljer tavlan eller räcker det med att den är undangömd i min källare aka databas?

Text kan omöjligen vara olagligt. Det finns ju rätt så sjuka böcker där ute..
Tills vi funnit ett svar på denan fråga har vi två alternativ;

- Kör bildgenerering lokalt. Då måste användaren själv godkänna användarvillkoren och tar eget ansvar.
Lagra inga bilder i databasen. Utifall att vi råkar generera olagligheter lokalt.
- Generera bilder med den politiskt korrekta fadersfiguren, Dall-E.

## Björn update

# Installation Guide for Illustrator Agent

## 1. Model Setup
1. Create a `/models` directory in your AdventureAI folder if it doesn't exist
2. Download the model from: https://civitai.com/models/133005?modelVersionId=920957
   - Select "Jugg_Xl_Lightning_by_RD" and click Download
3. Place the downloaded .safetensors file in the `/models` directory

## 2. Environment Setup
Add this line to your `.env` file (create it if it doesn't exist):
IMAGE_MODEL="juggernautXL_juggXILightningByRD"


## 3. Dependencies Installation
Run these commands in order:
```bash
# 1. Install PyTorch with CUDA 11.8 support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 2. Install required dependencies
pip install pillow
pip install diffusers
pip install python-dotenv
pip install safetensors
pip install transformers
pip install accelerate

# 3. Optional optimization (not supported on Windows)
pip install xformers  # Only for Linux/Mac