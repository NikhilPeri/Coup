import action
from player import Player
from game   import GameState

import random
import os

DebugMode = True
DebugMode = False

defaultNames = ["Leonardo", "Michaelengelo", "Raphael", "Donatello", "Splinter", "April"]

class ConsolePlayer(Player):
    def confirmCall(self, activePlayer, action): 
        """ return True if player confirms call for bluff on active player's action. returns False if player allows action. """
        choice = input ("\n%s, do you think %s's %s is a bluff?\n Do you want to call (Y/N)? " % (self.name, activePlayer.name, action.name))
        choice = choice.upper()
        
        if not choice in ('Y', 'N'):
            print (" Type Y or N.")
            return self.confirmCall(activePlayer, action)
            
        if choice == 'Y':
            return True
        
        return False
            
    def confirmBlock(self, opponentAction):
        """ returns action used by player to blocks action. return None if player allows action. """
        cardBlockers = []
        
        for card in GameState.CardsAvailable:
            if opponentAction.name in card.blocks:
                cardBlockers.append(card)

        print ("\n%s can be blocked with the following cards:" % (opponentAction.name))
        for i, card in enumerate(cardBlockers):
            print(" %i: %s" % (i + 1, card.name))
        print(" %i: (Do not block)" % (len(cardBlockers) + 1))
            
        choice = input("%s, do you wish to block %s? " % (self.name, opponentAction.name))
        if not choice.isnumeric():
            print (" Invalid choice, try again\n")
            return self.confirmBlock(opponentAction)
        choice = int(choice) - 1
        
        if choice == len(cardBlockers):
            return None         # player decides not to block
        
        if not (choice >= 0 and choice < len(cardBlockers)):
            print (" Invalid choice, try again\n")
            return self.confirmBlock(opponentAction)
            
        block = cardBlockers[choice - 1]
        
        print("\n%s is blocking with %s\n" % (self.name, block.name))
        return block
        
    def selectInfluenceToDie(self):
        """ select an influence to die. returns the value from the influence list. """
        # todo: raise notImplemented. should be overriden by the input class
        print ("\n%s has lost the challenge!" % (self.name))
        
        if len(self.influence) == 1:
            print ("%s will lose their last card, %s" % (self.name, self.influence[0].name))
            return self.influence[0]
        
        print ("%s, select influence to lose:" % (self.name))
        for i, card in enumerate(self.influence):
            print (" %i: %s" % (i + 1, card.name))
        choice = input("> ")
        if not choice.isnumeric():
            print ("Invalid choice, try again\n")
            return self.selectInfluenceToDie()
        choice = int(choice)
        if not (choice == 1 or choice == 2):
            print ("Invalid choice, try again\n")
            return self.selectInfluenceToDie()
        if choice > len(self.influence):
            print ("Invalid choice, try again\n")
            return self.selectInfluenceToDie()
            
        return self.influence[choice - 1]

    def selectAmbassadorInfluence(self, choices, influenceRemaining):
        """ returns one or two cards from the choices. """
        finalChoices = []
        
        def askChoice(choices, inputMessage):
            for i, choice in enumerate(choices):
                print (" %i: %s" % (i + 1, choice.name))
            card = input (inputMessage)
            
            if not card.isnumeric():
                return askChoice(choices)
                
            card = int(card) - 1
            if card < 0 or card >= len(choices):
                return askChoice(choices)
            
            card = choices[card]
            return card
        
        print("\n%s, these are the cards you drew:" % (self.name))
        
        card1 = askChoice(choices, "Select the first card to take>")
        choices.remove(card1)
        
        if (influenceRemaining == 1):
            return [card1]
        else:
            print("")
            card2 = askChoice(choices, "Select the second card to take>")
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
    
    def GetNumberOfPlayers():
        PlayerCount = input("How many players (2-6)? ")
        if not PlayerCount.isnumeric():
            return GetNumberOfPlayers()
        
        PlayerCount = int(PlayerCount)
        if PlayerCount < 2 or PlayerCount > 6:
            return GetNumberOfPlayers()
            
        return PlayerCount
        
    PlayerCount = GetNumberOfPlayers()
    #PlayerCount = 2        # for testing purposes

    def CreatePlayer(Number):
        player = ConsolePlayer()
        
        player.name = input("Player #%i: What is your name (Leave blank for a random name)? " % (Number))
        
        if player.name.strip() == "":
            player.name = random.choice(defaultNames)
            defaultNames.remove(player.name)
            print(" Player %i's name is %s\n" % (Number + 1, player.name))
                
        return player

    print("\n")
    for i in range(PlayerCount):
        Players.append(CreatePlayer(i))
        
    random.shuffle(Players)

    global PlayersAlive
    PlayersAlive = [player for player in Players if player.alive]
    
    SetupActions()

def PrintTurnOrder():
    print ("\nTurn order:")
    for i, player in enumerate(Players):
        print(" %i: %s" % (i + 1, player.name))

def PrintDeckList():
    print ("There are %i cards in the Court Deck" % (len(GameState.Deck)))
    
    if DebugMode:
        deck = [card.name for card in GameState.Deck]
        deck.sort()
        for card in deck:
            print(" ", card)

def PrintRevealedCards():
    size = len(GameState.RevealedCards)
    if size == 0:
        return
        
    print ("There are %i cards that has been revealed:" % (size))

    reveals = [card.name for card in GameState.RevealedCards]
    reveals.sort()
    for card in reveals:
        print(" ", card)

def MainLoop():
    # Infinite loop until one player remains
    global PlayersAlive, CurrentPlayer
    
    while len(PlayersAlive) > 1:
        player = Players[CurrentPlayer]
        
        def PrintInfo():
            os.system("cls")
            print("%s's turn (Coins: %i)" % (player.name, player.coins))
            print("=================\n ")
            PrintDeckList()
            PrintRevealedCards()
            print("\n%s's cards are: " % (player.name), end = "")
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
            
            global PlayersAlive 
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
            
            status = False
            
            def ChooseTarget():
                PossibleTargets = list(Players)
                PossibleTargets.remove(player)          #todo: remove this to test if the program handles targetting self
                
                #todo: add code to remove dead players from list.
                
                if len(PossibleTargets) == 1:
                    return PossibleTargets[0]
                
                for i, iterPlayer in enumerate(PossibleTargets):
                    print(" %i: %s" % (i + 1, iterPlayer.name))
                target = input ("Choose a target>")
                
                if not target.isnumeric():
                    return ChooseTarget()
                target = int(target) - 1
                if target < 0 or target >= len(PossibleTargets):
                    return ChooseTarget()
                
                return PossibleTargets[target]

            target = None
            if AvailableActions[move].hasTarget:
                target = ChooseTarget()

            try:
                status, response = player.play(AvailableActions[move], target)

                print("\n%s is playing %s" % (player.name, AvailableActions[move].name), end = '')
                if not target is None:
                    print(" (target: %s)" % (target.name))
                else:
                    print("")
            except action.ActionNotAllowed as e:
                print(e.message)
                ChooseAction()
                return
            except action.NotEnoughCoins as exc:
                print(" You need %i coins to play %s. You only have %i coins." % (exc.coinsNeeded, AvailableActions[move].name, player.coins))
                ChooseAction()
                return
            except action.BlockOnly:
                print("You cannot play %s as an action" % (AvailableActions[move].name))
                ChooseAction()
                return
            except action.TargetRequired:                        
                target = ChooseTarget()
                status, response = player.play(AvailableActions[move], target)
                
            if status == False:
                print (response)
            
        if player.alive:
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