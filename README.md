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
Spelet funkar!
Vi har inget sätt att rendera informationen på så bilderna öppnas direkt i windows.
Jag hoppas att pipelinen stängs när gameloopen breakar. Om inte så är det nog inget problem. Jag testade att kommentera ut den en gång och min dator lider inte av det i alla fall.
Spelet genererar nu text, bilder för varje prompt.
Dice rolls tas också i hänsyn och spelar faktiskt roll nu!

Bilderna sparas ingenstans. Om vi vill det så är det en enkel fix i antingen triage, illustrator eller main filen.

Nästa steg är att jobba på TTS och typannoteringar.
Sedan kommer vi till error handling.
Förslagsvis börjar vi error hantera i illustrator klassen abra för att förstå den bättre.



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