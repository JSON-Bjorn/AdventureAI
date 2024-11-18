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
Programmet är inte funktionellt.
Vi kan generera lite story från openAI.
Bildgenereringen funkar med test filen. Inte i main filen.
Nästa steg är att göra allting asyncronous.
Just nu är problemet att vi inte hinner generera bilden innan python försöker öppna den, så det borde vara en easy fix.

Steget efter det är att försöka få triage agent att kommunicera med sound agent.
Jag lyckades inte få till intended funktionalitet:
- Triage skickar context till Author.
- Author svarar med ny story. So far so good!
- Triage förmedlar nya storyn till Narrator (Här går det åt helvete)
- Narator ger tillbaka en wav fil.
Detta har troligtvis med att jag inte ger rätt tools till triage för att kunna skapa konversationer mellan agenterna.
Trioligtvis behöver vi göra en metod som appendar meddelanden och returnerar chat history mellan agents.

Vi behöver också uppdatera requirements filen.

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