#libraries imported
import random
from time import sleep
import sqlite3

#diferent cards, and the score for each
cardNumbers = ['A', '2', '3', '4', '5',
               '6', '7', '8', '9', '10', 'J', 'Q', 'K']
cardSuit = ['Diamonds', 'Spades', 'Clubs', 'Hearts']
cardScores = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
              '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}

#initializing global variables
money = 0

dealerCards = []
playerCards = []

played = []

doubled = False
special = False
specialOne = False

score = 0
dealerScore = 0
bet = 0

name = input('What is your name: ').lower()


def checkPlayers(name):
    global money

    #connecting to database
    conn = sqlite3.connect('databases/blackjDB.db')
    c = conn.cursor()

    #getting money from database using your name
    c.execute("select money from blackjPlayers where name = '{}'".format(name))
    value = c.fetchone()
    
    #if there isn't an item associated with the name
    if not value:
        
        #confirm that you want to create a new player
        confirm = input(f'{name} is not in database, do you want to create a new player (y/n): '.lower())
        
        #if you do, it inserts the player in the database, and gives a base amount of money
        if confirm == 'y' or confirm == 'yes':
            c.execute(
                """insert into blackjPlayers(name, money) values('{}', 10)""".format(name))
            conn.commit()
            c.execute("select money from blackjPlayers where name = '{}'".format(name))
            value = c.fetchone()
            conn.close()
            print('Created new player.')
        
        #if you don't, it asks for name again, and calls the function
        else:
            name = input('Enter your name: ')
            checkPlayers(name)

    else:
        confirm = 'y'
    
    #gets the amount of money you have
    if confirm == 'y' or confirm == 'yes':
        money = value[0]


def randomBeginning():
    global score, dealerScore, bet, money, specialOne, special

    #if money is 0, then it tells you, and you get kicked from the game
    if money == 0:
        print("You don't have any money, play next time.")
        quit()

    print('You have $' + str(money) + '.')
    print()

    #asks the amount of money you want to bet, and checks if its a valid input
    s = input('How much do you wanna bet: ')

    while s.isdigit() == False or int(s) > money or int(s) <= 0:
        print('Invalid input, try again.')
        print()
        s = input('How much do you wanna bet: ')

    bet = int(s)

    #shows the first dealer card, and stores the card into 'played' array
    print('Dealer card is: ')

    num, typ = random.randint(0, len(cardNumbers) - 1), random.randint(0, len(cardSuit) - 1)
    num1, typ1 = cardNumbers[num], cardSuit[typ]
    played.append([num, typ])

    #gets the card score, and checks if it is a 'special' ace
    #it then prints the card, and adds to 'dealerCards' arary
    dealerScore += cardScores[num1]

    card = num1 + ' of ' + typ1
    dealerCards.append(card)
    
    checkSpecialOne()
    
    print(card)
    print()
    sleep(2)

    #gets your cards, and checks if it has been used before
    print("Your cards are: ")

    for _ in range(2):
        number, suit = random.randint(0, len(cardNumbers) - 1), random.randint(0, len(cardSuit) - 1)
        number1, suit1 = cardNumbers[number], cardSuit[suit]
        typOfCard = [number, suit]

        while typOfCard in played:
            number, suit = random.randint(0, len(cardNumbers) - 1), random.randint(0, len(cardSuit) - 1)
            number1, suit1 = cardNumbers[number], cardSuit[suit]
            typOfCard = [number, suit]

        #gets the score, checks if its a 'special' ace, and adds it to 'playerCards' array
        #prints your cards
        score += cardScores[number1]

        card1 = number1 + ' of ' + suit1

        playerCards.append(card1)
        
        checkSpecial()
        
        played.append(typOfCard)
        print(card1)

    #prints the score, if it's a blackjack, calls 'dealersTurn'
    #else, it calls 'playerOptions'
    
    print('Your score is: {0}'.format(score))
    print()
    sleep(2)
    
    if score == 21:
        dealersTurn()
    else:
        playerOptions()


def playerHit():
    global score, played, specialOne, special

    #gets the suit and number of the card, and if it has already been played
    #it gets a different card until it hasn't been played
    number, suit = random.randint(0, len(cardNumbers) - 1), random.randint(0, len(cardSuit) - 1)
    number1, suit1 = cardNumbers[number], cardSuit[suit]
    typOfCard = [number, suit]

    while typOfCard in played:
        number, suit = random.randint(0, len(cardNumbers) - 1), random.randint(0, len(cardSuit) - 1)
        number1, suit1 = cardNumbers[number], cardSuit[suit]
        typOfCard = [number, suit]

    #appends card to 'played' and 'playerCards', and gets your score
    #checks if it can be a 'special' ace
    played.append(typOfCard)

    score += cardScores[number1]

    card = number1 + ' of ' + suit1
    playerCards.append(card)
    
    checkSpecial()

    #prints all your cards
    for i in range(len(playerCards)):
        print(playerCards[i])

    #if score over 21, tells you that you busted, prints cards
    #calls 'changeMoney'
    if score > 21:
        print()
        print('Bust, score: {0}'.format(score))
        print()
        print('You lost. Your cards: ')
        print()
        for i in range(len(playerCards)):
            print(playerCards[i])
        print()

        changeMoney(0, bet)

    #under 21, prints score, and then calls 'playerOptions'
    elif score < 21:
        print('Your score is: {0}'.format(score))
        sleep(2)
        print()
        playerOptions()
        print()

    #equals 21, prints score, and calls 'dealersTurn'
    else:
        print('Your score is: {0}'.format(score))
        sleep(2)
        print()
        dealersTurn()
        print()

#if player stands, it calls 'dealersTurn'
def playerStand():
    dealersTurn()


def dealersTurn():
    global dealerScore, bet

    #giving it instructions when to hit, this stands when it is a soft or hard 17
    #calls 'dealerHit'
    while dealerScore < 17:
        dealerHit()

    #if score greater than 21, says that the dealer busted, and prints all cards played
    #calls changeMoney to update your money
    if dealerScore > 21:
        print('Dealer bust')
        print()
        print('You won. Your cards: ')
        print()
        for i in range(len(playerCards)):
            print(playerCards[i])
        print()

        print('Dealer cards: ')
        print()
        for i in range(len(dealerCards)):
            print(dealerCards[i])

        print()

        changeMoney(bet, 0)

    #if dealer wins, prints that you lost and all cards, and changes the money
    elif dealerScore > score:

        print('You lost. Your cards: ')
        print()
        for i in range(len(playerCards)):
            print(playerCards[i])
        print()

        print('Dealer cards: ')
        print()
        for i in range(len(dealerCards)):
            print(dealerCards[i])
        print()

        changeMoney(0, bet)

    #if you win, prints that you win, and calls 'changeMoney' to add money to your player
    elif score > dealerScore:
        print('You won. Your cards: ')
        print()
        for i in range(len(playerCards)):
            print(playerCards[i])
        print()

        print('Dealer cards: ')
        print()
        for i in range(len(dealerCards)):
            print(dealerCards[i])

        print()

        changeMoney(bet, 0)

    #if its a tie, prints that its a push
    else:
        print('Push')
        print()
        for i in range(len(playerCards)):
            print(playerCards[i])
        print()

        print('Dealer cards: ')
        print()
        for i in range(len(dealerCards)):
            print(dealerCards[i])
        print()


def playerOptions():
    global bet, doubled

    #opportunity for when doubling is shown as one of the option
    if 9 <= score <= 11 and len(playerCards) == 2 and bet * 2 <= money:
        double = input('Do you wanna double (y/n): ')
        
        #if answer is 'yes' or 'y', it makes 'doubled' true, doubles the bet, and hits once
        if double.lower() == 'yes' or double.lower() == 'y':
            doubled = True
            bet *= 2
            playerHit()

    #if doubled equals true, it goes to the dealers turn
    if doubled:
        dealersTurn()
        return

    #gets input from player
    playerChoice = input('Stand or Hit: ')
    print()

    #if its 'hit', it calls 'playerHit'
    if playerChoice.lower() == 'hit':
        playerHit()

    #if its 'stand', calls 'playerStand'
    elif playerChoice.lower() == 'stand':
        playerStand()

    #else, it prints that its invalid, and calls 'playerOption'
    else:
        print('Invalid input')
        print()
        playerOptions()


def dealerHit():

    global dealerScore, played, special, specialOne

    #gets the suit and number of the card, and if it has already been played
    #it gets a different card until it hasn't been played
    number, suit = random.randint(0, len(cardNumbers) - 1), random.randint(0, len(cardSuit) - 1)
    card1, suit1 = cardNumbers[number], cardSuit[suit]
    typOfCard = [number, suit]

    while typOfCard in played:
        number, suit = random.randint(0, len(cardNumbers) - 1), random.randint(0, len(cardSuit) - 1)
        card1, suit1 = cardNumbers[number], cardSuit[suit]
        typOfCard = [number, suit]

    #appends card to 'played' and 'dealerCards', and gets the dealer's score
    #checks if it can be a 'special' ace
    played.append(typOfCard)

    dealerScore += cardScores[card1]
    card = card1 + ' of ' + suit1
    dealerCards.append(card)

    checkSpecialOne()

    #prints the card and score
    print('Dealer gets: {0}'.format(card))
    print('Score: {0}'.format(dealerScore))
    sleep(2)
    print()


def changeMoney(gain, loss):
    global money, name

    conn = sqlite3.connect('databases/blackjDB.db')
    c = conn.cursor()

    #if gain equals 0, it means that you lost, and gets the amount you have remaining
    if gain == 0:
        moneyLeft = money - loss

    #else, it adds your bet to your money
    else:
        moneyLeft = money + gain

    #updates your money in the database
    c.execute(
        '''update blackjPlayers
            set money = {}
            where name = '{}'
        '''.format(moneyLeft, name))

    conn.commit()
    conn.close()

    #prints remaining amount
    print('You have ${0}.'.format(moneyLeft))
    print()


def newGame():
    global money, bet, dealerCards, playerCards, played, score, dealerScore, doubled, special, specialOne

    #restarts a new game, making the variables back to the original
    checkPlayers(name)

    bet = 0
    score = 0
    dealerScore = 0

    played = []

    dealerCards = []
    playerCards = []

    doubled = False
    specialOne = False
    special = False

    randomBeginning()

def checkSpecial():
    global score, playerCards, special
    
    #checks if there is an ace, and if score is less than 11
    if ('A of Spades' in playerCards or 'A of Clubs' in playerCards or 'A of Hearts' in playerCards or 'A of Diamonds' in playerCards) and score < 11:
        #if it is, adds 10 to your score, and makes 'special' equal true
        score += 10
        special = True
    
    #if 'special' is true, and score is over 21, it makes the ace equal 1 instead of 10
    #makes 'special' false
    elif special == True and score > 21:
        score -= 10
        special = False

def checkSpecialOne():
    global dealerScore, dealerCards, specialOne

    #checks if there is an ace, and if score is less than 11
    if ('A of Spades' in dealerCards or 'A of Clubs' in dealerCards or 'A of Hearts' in dealerCards or 'A of Diamonds' in dealerCards) and dealerScore < 11:
        #if it is, adds 10 to the dealers score, and makes 'specialOne' equal true
        dealerScore += 10
        specialOne = True
    
    #if 'specialOne' is true, and score is over 21, it makes the ace equal 1 instead of 10
    #makes 'specialOne' false
    elif specialOne == True and dealerScore > 21:
        dealerScore -= 10
        specialOne = False


#starts the game
checkPlayers(name)
randomBeginning()

#asks if you want to play again
while True:
    choice = input('Do you want to play again (y/n): ')

    #if your money is 0, it tells you that you don't have enough, and quits
    if money == 0:
        print('Not enough money. Good bye!')
        quit()

    #if you want to play again, it calls 'newGame'
    if choice.lower() == 'yes' or choice.lower() == 'y':
        print()
        newGame()
    
    #if you don't, it prints a goodbye message, and quits
    else:
        print('Thank you. Good bye!')
        quit()
