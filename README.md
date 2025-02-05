# Allmän info om denna branch
Denna branchen är för tillfället enbart för att kunna köra spelet lokalt men vi planerar att kunna kombinera denna med vår webbapplikation.

# Setup
Clona repot och kör filen start.bat för att installera alla nödvändiga paket.

# Current state
Spelet funkar!

Bilderna sparas ingenstans. Om vi vill det så är det en enkel fix i antingen triage, illustrator eller main filen.

## Björn update

# Installation Guide for Illustrator Agent

## 1. Model Setup
1. Create a `/models` directory in your AdventureAI folder if it doesn't exist
2. Download the model from: https://civitai.com/models/133005?modelVersionId=920957
   - Select "Jugg_Xl_Lightning_by_RD" and click Download
3. Place the downloaded .safetensors file in the `/models` directory

## 2. Environment Setup
Add these lines to your `.env` file in root (create it if it doesn't exist):
IMAGE_MODEL="juggernautXL_juggXILightningByRD"
OPEN_AI_API_KEY="sk-proj-..."


## 3. Run the application

Starta spelet genom att köra filen quickstart.bat