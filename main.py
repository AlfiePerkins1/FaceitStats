import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time
import config


def getFaceitID():

    payload = {}
    headers = {
        'Authorization': config.api_key,
    }

    FaceitNickname = input("Enter faceit nickname")
    amountOfGames = int(input("Enter number of games to search"))

    # Getting faceit ID
    URL = f"https://open.faceit.com/data/v4/players?nickname={FaceitNickname}&game=csgo="

    response = requests.request("GET", URL, headers=headers, data=payload)
    data = response.json()
    playerID = data['player_id']
    playerSteamID = data['steam_id_64']

    Menu(playerID, amountOfGames, FaceitNickname, playerSteamID)


def getFaceitMatchHistory(playerID, limit,FaceitNickname):
    matchID = []
    payload = {}
    headers = {
        'Authorization': config.api_key,
    }

    # Getting match history
    URL = f"https://open.faceit.com/data/v4/players/{playerID}/history?game=csgo&offset=0&limit={limit}"

    response = requests.request("GET", URL, headers=headers, data=payload)
    data = response.json()

    print(data['items'][0]['match_id'])

    x = 0
    for x in range(limit-1):
        matchID.append(data['items'][x]['match_id'])
        print(matchID[x])

    getFaceitMatchStats(matchID, limit, FaceitNickname)


def getFaceitMatchStats(matchIDArray, limit, FaceitNickname):

    EnemyElo = []
    myElo = []
    myTeam = []
    payload = {}
    headers = {
        'Authorization': config.api_key,
    }

    for x in range(len(matchIDArray)):
        j = 0
        print(f"Game {x} ID: {matchIDArray[x]}")
        # Getting match history
        URL = f"https://open.faceit.com/data/v4/matches/{matchIDArray[x]}"



        response = requests.request("GET", URL, headers=headers, data=payload)
        data = response.json()
        #Check to see if the game is a hub
        if data['competition_type'] == "hub":
            print(f"Game {x} is a hub game, no average elo")
        else:
              # Loop through players from Team 1
            Team1Names = []
            while j in range(5):
                Team1Names.append(data['teams']['faction1']['roster'][j]['nickname'])
                j += 1
            if FaceitNickname in Team1Names:
                try:
                    myTeam.append(True)
                    EnemyElo.append(data['teams']['faction2']['stats']['rating'])
                    #print(f"Elo for enemy team(not my team) {EnemyElo[x]}")

                    myElo.append(data['teams']['faction1']['stats']['rating'])
                    #print(f"Elo for my team {myElo[x]}")
                except:
                    print("No average elo")
            else:
                try:
                    myTeam.append(False)
                    EnemyElo.append(data['teams']['faction1']['stats']['rating'])
                    #print(f"Elo for enemy team {EnemyElo[x]}")

                    myElo.append(data['teams']['faction2']['stats']['rating'])
                    #print(f"Elo for my team {myElo[x]}")
                except:
                    print("No average elo")
        #print(myTeam[x])

    MakeEloGraph(EnemyElo,myElo, FaceitNickname)


def MakeEloGraph(EnemyElo, myElo, FaceitNickname):

    m, b = np.polyfit(EnemyElo, myElo, 1)

    point1 = m*min(EnemyElo) + b
    point2 = m*max(EnemyElo) + b

    #plt.style.use('dark_background')
    plt.scatter(EnemyElo,myElo)
    plt.title(f"Elo Balancing for {FaceitNickname}")
    plt.xlabel('Enemy Elo')
    plt.ylabel(f"{FaceitNickname}'s team elo")
    plt.legend(['Regression Line: y = {:.2f}x + {:.2f}'.format(m, b)])
    #plt.plot(EnemyElo, m*EnemyElo+b, color='red')
    plt.plot([min(EnemyElo),max(EnemyElo)],[point1,point2], 'k--')
    plt.grid(True)
    plt.show(block=True)
    plt.yscale('linear')
    print('Printed')



def Menu(playerID, amountOfGames, FaceitNickname, playerSteamID):
    print("Options:")
    print("1. Average Elo comparison")
    print("2. Elo compared with games graph")

    print("")
    print(f"Faceit ID {playerID}")

    choice = int(input("Pick an option"))
    if choice == 1:
        getFaceitMatchHistory(playerID, amountOfGames, FaceitNickname)
    if choice == 2:
        ScrapeFaceitFinder(playerID,amountOfGames, FaceitNickname, playerSteamID)





def ScrapeFaceitFinder(playerID,amountOfGames, FaceitNickname, playerSteamID):
    # data = pd.read_csv(f"PlayerStats/{FaceitNickname}.csv")
    #
    #
    # data = data.drop("web-scraper-order",axis=1)
    # data = data.drop("web-scraper-start-url",axis=1)
    data = scrape(playerSteamID)
    #print(f"THIS IS THE DATA {data}")
    data["#"] = data["#"].astype('int')
    data.sort_values(['#'],inplace=True)

    data = data[data.ELO != "—"]

    data['ELO'] = data['ELO'].str.replace(r'\([^()]*\)','',regex=True)

    data['ELO'] = pd.to_numeric(data['ELO'])

    #Split Data to how many games
    data = data.iloc[:amountOfGames]
    print(data)
    data.to_csv('testData.csv', index =False)
    createGraph(data, FaceitNickname)

def createGraph(data, FaceitNickname):
    plt.plot(data['#'],data['ELO'], color='r')
    plt.xlabel("Game Number")
    plt.ylabel("Elo")
    plt.title(f"Elo compared with game number for {FaceitNickname}")
    plt.grid()
    plt.plot()
    plt.show()

def scrape(steamID):

    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    url = f"https://faceitfinder.com/stats/{steamID}/matches/1"
    response = requests.get(url, headers=HEADERS)
    print(response)

    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', class_ = 'matches_table')
    #print(table)

    headers = []

    for i in table.find_all('th'):
        title = i.text
        headers.append(title)
        #print(title)

    scrapedData = pd.DataFrame(columns=headers)

    #First page
    for j in table.find_all('tr')[1:]:
        row_data = j.find_all('td')
        row = [i.text for i in row_data]
        length = len(scrapedData)
        scrapedData.loc[length] = row

    #print(scrapedData)

    # Get match number
    gameNum = int(scrapedData.iloc[0,0])
    numOfPages = int(gameNum / 20) + 1

    for i in range(numOfPages):
        HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

        url = f"https://faceitfinder.com/stats/{steamID}/matches/{i}"
        response = requests.get(url, headers=HEADERS)
        print(response)
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', class_='matches_table')

        for j in table.find_all('tr')[1:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]
            length = len(scrapedData)
            scrapedData.loc[length] = row
        time.sleep(0.5)

    print(scrapedData)
    return scrapedData

if __name__ == "__main__":
    getFaceitID()
    #scrape()

