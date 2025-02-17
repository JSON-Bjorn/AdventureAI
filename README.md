Jag håller på att skriva om backend i på denna branch.

# Progress
### Current
- Vi connectar till SD API
    - SD API är optimiserad.
    - Vi behöver dock optimisera initieringen av pipeline (triton?)
- sd_test.py öppnar bilder. sweet.

### Next
- Gör en mi_test.py för LLM API
- Implementera LLM och SD API i game loop
- Connecta skiten till frontend och se o mvi får fram bild och text


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