# Allmän info om denna branch
Den här branchen är tänkt för att fungera för att kunna köra spelet lokalt. För tillfället kommer vi inte göra några större ändringar i denna branch.

# Setup
- Se till att köra start.bat för att installera alla nödvändiga paket.

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


# Installation Guide for Illustrator Agent

## 1. Model Setup
1. Create a `/models` directory in your AdventureAI folder if it doesn't exist
2. Download the model from: https://civitai.com/models/133005?modelVersionId=920957
   - Select "Jugg_Xl_Lightning_by_RD" and click Download
3. Place the downloaded .safetensors file in the `/models` directory

## 2. Environment Setup
Add these lines to your `.env` file (create it if it doesn't exist):
OPENAI_API_KEY="sk-proj-****************"
IMAGE_MODEL="juggernautXL_juggXILightningByRD"