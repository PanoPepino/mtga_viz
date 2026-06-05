

# MTGA Visualisation Tool
---

Package to create clean dashboards for competitive gaming for MTG Arena.

It targets three different competitive modes in MTG Arena:

- _Ladder_: Collect your own data (or with friends), and explore how well your chosen deck performs against decks you find in the ladder 

- _Metagame_: Do you want to collect and display data on plenty of runs of a given Metagame Challenge? 

- _Tournament_: Mother of competitions. Gather information and display insightful data in the form of match matrices, overall win rate vs presence and more.



(See attached images for expected dashboard for each mode)
## Usage instructions

(Under Construction)





<!-->

# TO DO

Target: Create a package for easy visualisation for MTGA competitive gaming. 

How: It should have 3 main components: 
        - Ladder: Collect and display information on your (or shared run) along the ladder matches.
        - Metagame: Use Metagame challenges data to share information on rounds and decks.
        - Tournament: Use tournament information (aggregrated) to display match matrix and so on.

Detail:

    - Ladder: Simply collected data to be displayed:
        1) WR vs Meta % (Both for archetype and deck)
        2) Match up Breakdown (i.e. # times 2-0,2-1, etc) (Both for archetype and deck)
           (Add WR OTP/OTD)?

    - Metagame: 
        1) Overall Meta % (Both for archetype and deck)
        2) WR vs Meta % (Both for archetype and deck)
        3) Heat map for runs. X = wins; Y = decks. For each X-position:
            a) Display gradient colors in each square, based on the normalisation respect to 1.
            b) Display gradient colors + vary its height wrt the normalised value.
    
    - Tournament:
        1) Overall Meta % (Just Deck)
        2) WR vs Meta % (Just Meta)
        3) Match matrix (avoid mirrors. Grade by confidence)
        4) Confidence interval for each deck

    

- Fix titles in dashboard
- Clean code
- Restructure package
- Create the cli part

<-->

