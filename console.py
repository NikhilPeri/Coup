import action
from player import Player
from game   import GameState

import random
import os

class ConsolePlayer(Player):
    def selectAmbassadorInfluence(self, choices, influenceRemaining):
        finalChoices = []
        
        def askChoice(choices):
            for i, choice in enumerate(choices):
                print ("%i: %s" % (i + 1, choice.name))
            card = input ("Select a card> ")
            
            if not card.isnumeric():
                return askChoice(choices)
                
            card = int(card) - 1
            if card < 0 or card >= len(choices):
                return askChoice(choices)
            
            card = choices[card]
            print ("Selected %s" % (card.name))
            return card
            
        card1 = askChoice(choices)
        choices.remove(card1)
        
        if (influenceRemaining == 1):
            return [card1]
        else:
            card2 = askChoice(choices)
            return [card1, card2]
        

Players = []
PlayersAlive = []
CurrentPlayer = 0

AvailableActions = []
def SetupActions():
    global AvailableActions
    for action in GameState.CommonActions:
        AvailableActions.append(action)
    for action in GameState.CardsAvailable:
        AvailableActions.append(action)

def Setup():
    # How many people are playing?
    # Generate the player list
    # Shuffle the player list

    GameState.reset()
    #PlayerCount = int(input("How many players? "))
    PlayerCount = 2

    def CreatePlayer(Number):
        player = ConsolePlayer()
        
        print("Creating Player #%i" % (Number + 1))
        #player.name = input(" What is your name? ")
        player.name = random.choice(["A", "B", "C"]) + str(Number)
        
        return player

    for i in range(PlayerCount):
        Players.append(CreatePlayer(i))
        
    random.shuffle(Players)

    global PlayersAlive
    PlayersAlive = [player for player in Players if player.alive]
    
    SetupActions()

def PrintTurnOrder():
    print ("Turn order:")
    for i, player in enumerate(Players):
        print(" %i: %s" % (i + 1, player.name))

def PrintDeckList():
    print ("Cards in Court Deck (%i cards):" % (len(GameState.Deck)))
    deck = [card.name for card in GameState.Deck]
    deck.sort()
    for card in deck:
        print(" ", card)

def MainLoop():
    # Infinite loop until one player remains
    global PlayersAlive, CurrentPlayer
    
    while len(PlayersAlive) > 1:
        player = Players[CurrentPlayer]
        
        def PrintInfo():
            os.system("cls")
            print("%s's turn" % player.name)
            print(" Coins: %i" % player.coins)
            print("=================\n ")
            PrintDeckList()
            print("\nCards in hand of %s: " % (player.name), end = "")
            print(" and ".join([card.name for card in player.influence]))
            print()

        def PrintActions():
            print("Available actions:")
            for i, action in enumerate(AvailableActions):
                print (" %i: %s" % (i + 1, action.name))
        
        def Cleanup():
            global CurrentPlayer
            CurrentPlayer += 1
            if CurrentPlayer >= len(Players): CurrentPlayer = 0
            PlayersAlive = [player for player in Players if player.alive]
        
        def ChooseAction():    
            move = input ("Action> ")
            if not move.isnumeric():
                ChooseAction()
                return
            move = int(move) - 1
            
            if not (move >= 0 and move < len(AvailableActions)):
                ChooseAction()
                return
            
            print("Playing %s" % AvailableActions[move].name)
            try:
                status, response = player.play(AvailableActions[move])
            except action.TargetRequired:
                def ChooseTarget():
                    for i, player in enumerate(Players):
                        print(" %i: %s" % (i + 1, player.name))
                    target = input ("Choose a target>")
                    
                    if not target.isnumeric():
                        return ChooseTarget()
                    target = int(target) - 1
                    if target < 0 or target >= len(Players):
                        return ChooseTarget()
                    
                    return target
                        
                target = ChooseTarget()
                status, response = player.play(AvailableActions[move], Players[target])
                
            if status == False:
                print (response)
                ChooseAction()
            
        
        PrintInfo()
        PrintActions()
        ChooseAction()
        Cleanup()
        input("\nPress enter key to continue...")
        
    print("\nThe winner is %s" % (PlayersAlive[0].name))

os.system("cls")
Setup()
PrintTurnOrder()
input("\nPress enter key to start...")
MainLoop()