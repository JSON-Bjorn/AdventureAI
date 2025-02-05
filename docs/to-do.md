# Move SD prompt making out of the triage class

# Increase stories in memory.
Have all generated stories in a dict.
reference this every time we need to generate a story.
Save the dict to cloud when we end the game
summarize each story after they have taken place.
keep the most recent generated story uncompressed.

# Improve SD prompting.
problem:
We are still having issues with reaching the token limit.
We could have another LLM class to handle the SD prompt.
Make it explicit and learn it how to write proper juggernaut prompts.

Vi får bra bilder på:
- landscapes
- anatomy (ibland, the occational ai fuckup med ett extra ben)

Vi får dåliga bilder på:
- ansikten
- gräs av någon anledning
- detaljerade saker
    (overall image looks good, but details are bad)

Lösning:
Håller på med denna nu.
Vad jag gjort:
- förminskat prompt-storlek med 30% (vi slår i taket och truncatear hela tiden)
- Flyttat all prompt engineering till 'prompt engineer' klassen
    Här skapar vi base prompt från story, bestämmer vad som är i mitten av bilden och tilldelar en kategori, lägger till enhancements baserat på kategori, skickar färdig prompt till SD.







# Loras?
We need to shorten the fuck out of the prompt.
Hard cap on 50 tokens to leave place for loras.
Triage identifies if the scene should contain a lora.
Boolean value is sent to SD agent.
Sd agent concatenates the prompt with the lora calling phrase and a hardcoedd weight.
Put the loras at the start of the prompt to avoid truncating them from the prompt.

# Make dice rolls happen slightly more frequent (dont use ai for this, hes is just gonna fuck it up)


# Migrate to react frontend
- Det här har kommit a looong way idag.
Vi har faktiskt en fungerande frontend nu.
Mycket buggar, inte interagerbar alls.
Men vi kan starta ett spel och få fram texten.
Bilderna genereras, alla api calls görs men ljudfilerna samd bilden når aldrig frontend.
Behövde lite hjälp så ai har lagt till en massa onödigt shit.
Exempelvis så sparar vi alla bilder i static/images.
Samt ljudfiler i static/audio.
Det här måste väck vid nästa code session.
Just nu har jag tatgit bort dem så att vi inte pushar ut 253 bilder på github.

