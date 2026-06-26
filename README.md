

# MTGA Visualisation Tool
---

Package to create clean and insightful dashboards for competitive gaming for MTG Arena. 

It targets 2 different competitive modes in MTG Arena:

- _Ladder_: Based on any collected database with ladder results, display interesting 
- _Metagame_: Do you want to collect and display data on plenty of runs of a given Metagame Challenge? 


## Usage instructions

(Under Construction)





<!--

# To Do

# Idea of package

Target: Create a package for easy visualisation for MTGA competitive gaming. 

How: It should have 3 main components: 
        - Ladder: Collect and display information on your (or shared run) along the ladder matches.
        - Metagame: Use Metagame challenges data to share information on rounds and decks.
        - Tournament: Use tournament information (aggregrated) to display match matrix and so on.

Detail:

    - Ladder: Simply collected data to be displayed. Ideal columns:
    (timestamp | user_name | user_deck | oppo_deck | result)

        Plots to draw:
        1) Overall Archetypes piloted in ladder + sub pies with main decks piloted for each archetype
        2) WR vs Meta % per Arch w/ confidence levels
        3) WR vs Meta % per deck (with threshold) & confidence levels
        4) Top X decks w/ overall WR w/ error and confidence levels.
        5) Top X decks vs Y other decks, W-L breakdown (2-0, 2-1, etc) with # games 
        6) Match Matrix for Top X decks with confidence levels.
        

    - Metagame. Ideal columns:
    (timestamp | user_name | user_deck | run result | oppo_deck | result)

        Plots to draw:
        1) Overall Archetypes piloted in metagame challenge + sub pies with main decks piloted for each archetype
        2) WR vs Meta % per Arch w/ confidence levels
        3) WR vs Meta % per deck (with threshold) & confidence levels
        4) Top X decks w/ overall WR w/ error and confidence levels.
        5) Top X decks vs Y other decks, W-L breakdown (2-0, 2-1, etc) with # games 
        6) Match Matrix for Top X decks with confidence levels.
        7) curves of % share per top X decks vs timestamp (1h interval), with some fancy point signaling when a player got a trophy (i.e. a 7-0 run)
        8) Normalised runs to 1 -> histogram showing % of 0-1, % of 1-1 and so on up to % of 7-0 for top X decks.
        9) Info-graphics of trophys for those user. (i.e. Manolo -> 2 Trophies (Mardu Energy and Tempo), etc)
        



    - Tournament (TO be CONSIDERED IN THE FUTURE):
        1) Overall Meta % (Just Deck)
        2) WR vs Meta % (Just Meta)
        3) Match matrix (avoid mirrors. Grade by confidence)
        4) Confidence interval for each deck

    

- Fix titles in dashboard
- Clean code
- Restructure package
- Create the cli part

-->

