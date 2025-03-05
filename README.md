Jag håller på att skriva om backend i på denna branch.

# Progress
### Current
Nästan hela backend har blivit refactored efter min första refactor.
Det går inte längre att testa spelet i terminalen, nästa gång kör vi med frontend testing!
Endpointen ligger uppe och är kopplad till get_next_scene funktionen i GameSession klassen.

Jag har även flyttat på prompt building till en egen klass.
Tanken är att generative_apis.py bara ska hålla api call funktioner.
Vi bör slå ihop dessa klasser. 1 klass med 3 methods är bttre än 3 klasser med 1 method var.



### Next
- Testa mot frontend och se om det funkar.
Har låtit Claude simulera requests till /start_new_game några gångeroch den hittar inga fel.

Ny ide för hur dice rolls hanteras i frontend.
Problemet med nuvarande version är att det inte känns interaktivt.
Vi skriver in vad vivill göra och sedan får vi bara nästa story
Så här gör vi istället för att simulera att användaren faktiskt rullar tärningen:
    - Frontend gör request till endpoint
    - Dice rolls hanteras här (success eller ej)
    - Response kommer till frontend
    - Vi visar inte response förens användaren klickar på tärningen.
    - Användaren klickar, vi visar resultatet.
    - Det känns som att användaren har rullat tärningen och att det hände nyss
    - Rendera resten.
    - Profit
    - Buy a boat


# Frontend BAckend interaktion explained

- Spelaren väljer en starting point för sin story.
Den ser ut så här:
```python
starting_point_example = {
    "protagonist_name": "Felix",
    "inventory": [],
    "scene": {
        "story": "You are a cat",
        "action": "You meow at the mouse",
        "starting_point": True,
    }
}
```

- Frontend sparar den i zustand store
```python
zustand_example = {
    "game_session": {
        "protagonist_name": "Felix",
        "inventory": [],
        "scenes": [
            {
            "story": "You are a cat",
            "action": "You meow at the mouse",
            "starting_point": True,
            },
        ]
    }
}
```

- Frontend gör en request till /start_new_game i backend.
```python
call_backend_api(scenes=zustand_example["game_session"]) # Hela game session!
```

- Backend instantierar GameSession klassen och kör get_next_scene metoden.
Till slut så returnerar vi detta:
```python
{
    "story": str, # Visas för spelaren
    "compressed_story": str, # Sparas till zustand store
    "image": str, # Visas för spelaren
    "music": str, # Spelas upp tills frontend tar emot en ny path (logiken sker i frontend)
    "dice_threshold": int, # Visas på skärmen
    "dice_success": bool, # Visas på skärmen
    "dice_roll": int, # Visas på skärmen
}
```

- Sean uppdaterar vi zustand store i frontend med komprimerade stories
```python
zustand_example = {
    "game_session": {
        "protagonist_name": "Felix",
        "inventory": [],
        "scenes": [
            {
                "story": "You are a cat",
                "action": "You meow at the mouse",
                "starting_point": True,
            },
            {
                "story": "The mouse runs away", # Den nya storyn från backend
            },
        ]
    }
}
```

- Använndaren anger sitt nya val: "I chase the mouse"
Vi lägger till detta i zustand store och sedan requestar vi '/get_new_scene' igen
```python
zustand_example = {
    "game_session": {
        "protagonist_name": "Felix",
        "inventory": ["Mouse soul"],
        "scenes": [
            {
                "story": "You are a cat",
                "action": "You meow at the mouse",
                "starting_point": True,
            },
            {
                "story": "You catch the mouse!",
                "action": "I eat the mouse",
            },
        ]
    }
}
```


