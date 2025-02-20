Jag håller på att skriva om backend i på denna branch.

# Progress
### Current
Mistral och SD funkar bra med test filerna.
Har gjort en test_game_loop.py där vi testar köra game loop och rendera i temrinalen
Kommer till bildgenereringen. Vi får 200ok från API.


### Next
Fortsätt emd game loop test.
Skriv en instruction för prompt generring innan vi anropar sd api.
Senaste error som jag inte orkade titta på: 
```bash
  File "C:\Users\Felix\Desktop\Code\Egna projekt\AdventureAI - Full project\backend\src\game\game_loop.py", line 96, in game_loop
    await self.render_scene(self, scene)
          ^^^^^^^^^^^^^^^^^
AttributeError: 'GameSession' object has no attribute 'render_scene'
```


# The new flow
- Landing page 1
- Login/Create account (kan bara vara username/password for now)
- Landing page 2 
    - New game
        - User is prompted to choose:
            - Name
            - Starting location
            - What they are doing
            - One thing in their inventory
        - Game loop is started
    - Continue game
        - Previous game data is fetched from db
        - Game loop is started


# Miro Dashboard
[Click me](https://miro.com/welcomeonboard/ellHZVJQdGhmMGF4dE9TeStSRVdKemRTQ293Y1VRNmlPeWQzMkltQ3RLalovUlJwc0t6M1d2eEd1eGViOTJ4VExTenhNNW9KSFRtQ3M4T25oSS9Cc01nem12L210Z3VNTWV0Q2hMSjlFRlVuMVQwUTY5cE1MdnU0QzRnL2JvWEJ3VHhHVHd5UWtSM1BidUtUYmxycDRnPT0hdjE=?share_link_id=543009961199)