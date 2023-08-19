#API Key 3c4e8343-365e-4a93-86ac-cfffbb47ff70

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import time
import config
import os


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


def getFaceitMatchHistory(playerID, limit,FaceitNickname, graph):
    matchID = []
    offset = 0
    loopIndex = limit /100
    i = 0
    payload = {}
    headers = {
        'Authorization': config.api_key,
    }
    #Limit of 100 games per request

    while i < loopIndex:
        # Getting match history
        URL = f"https://open.faceit.com/data/v4/players/{playerID}/history?game=csgo&offset={offset}&limit=100"

        response = requests.request("GET", URL, headers=headers, data=payload)
        data = response.json()

        print(data['items'][0]['match_id'])

        x = 0
        for x in range(100):
            matchID.append(data['items'][x]['match_id'])
            print(matchID[x])

        offset += 100
        time.sleep(2)
        i+=1

    getFaceitMatchStats(matchID, limit, FaceitNickname, graph)



def getFaceitMatchStats(matchIDArray, limit, FaceitNickname, graph):

    EnemyElo = []
    myElo = []
    myKD = []
    myKR = []
    myHSP = []
    myKills = []
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

        # Get the stats for the game
        StatsURL = f"https://open.faceit.com/data/v4/matches/{matchIDArray[x]}/stats"
        StatsResponse = requests.request("GET", StatsURL, headers=headers, data=payload)
        StatsData = StatsResponse.json()

        #Find player ID
        i = 0
        playerNum = 0
        playerTeam = 0
        for i in range(5):
            try:
                if StatsData['rounds'][0]['teams'][1]['players'][i]['nickname'] == FaceitNickname:
                    playerNum = i
                    playerTeam = 1
                    print(f"Found, playerID of {i} team 1")
                elif StatsData['rounds'][0]['teams'][0]['players'][i]['nickname'] == FaceitNickname:
                    playerNum = i
                    playerTeam = 0
                    print(f"Found, playerID of {i} team 0")
                else:
                    pass
                i += 1
            except:
                #Occurs when a player left the game
                ("Only 4 players on team")


        #Check to see if the game is a hub
        if data['competition_type'] == "hub":
            print(f"Game {x} is a hub game, no average elo")
        else:
            try:
                  # Loop through players from Team 1
                Team1Names = []
                while j in range(5):
                    Team1Names.append(data['teams']['faction1']['roster'][j]['nickname'])
                    j += 1
                if FaceitNickname in Team1Names:
                    try:
                        myTeam.append(True)
                        EnemyElo.append(data['teams']['faction2']['stats']['rating'])

                        myElo.append(data['teams']['faction1']['stats']['rating'])

                        #Add stats here
                        KD = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["K/D Ratio"]
                        KR = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["K/R Ratio"]
                        HSP = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["Headshots %"]
                        Kills = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["Kills"]
                        myKD.append(KD)
                        myKR.append(KR)
                        myHSP.append(HSP)
                        myKills.append(Kills)
                        print(f"Appended for game ID {matchIDArray[j]}, KD: {KD}, KR: {KR}, HSP: {HSP}, Kills: {Kills} ")

                    except:
                        print("No average elo")
                else:
                    try:
                        myTeam.append(False)
                        EnemyElo.append(data['teams']['faction1']['stats']['rating'])

                        myElo.append(data['teams']['faction2']['stats']['rating'])

                        # Add stats here
                        KD = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["K/D Ratio"]
                        KR = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["K/R Ratio"]
                        HSP = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["Headshots %"]
                        Kills = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats']["Kills"]
                        myKD.append(KD)
                        myKR.append(KR)
                        myHSP.append(HSP)
                        myKills.append(Kills)
                        print(f"Appended for game ID {matchIDArray[j]}, KD: {KD}, KR: {KR}, HSP: {HSP}, Kills: {Kills} ")

                        #print(f"Elo for my team {myElo[x]}")
                    except:
                        print("No average elo")

            except:
                print("Player not found")

    if graph == "elo":
        MakeEloGraph(EnemyElo,myElo, FaceitNickname)
    if graph == "stats":
        for i in range(len(KD)):
            print(EnemyElo[i])
            print(myKD[i])
            print(myKR[i])
            print(myHSP[i])
            print(myKills[i])

        MakeStatsGraph(EnemyElo, myKD, myKR, myHSP, myKills, FaceitNickname)



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

def MakeStatsGraph(EnemyElo, KD, KR, HSP, Kills, FaceitNickname):

    print(KD[0])
    EnemyElo = [int(x) for x in EnemyElo]
    KD = [float(x) for x in KD]
    KR = [float(x) for x in KR]
    HSP = [float(x) for x in HSP]
    Kills = [float(x) for x in Kills]

    plt.scatter(EnemyElo, KD)
    plt.grid(True)
    plt.xlabel("Enemy Elo")
    plt.ylabel(f"KD for {FaceitNickname}")
    plt.show(block=True)


def Menu(playerID, amountOfGames, FaceitNickname, playerSteamID):
    print("Options:")
    print("1. Average Elo comparison")
    print("2. Elo compared with games graph")
    print("3. Stats Graph")

    print("")
    print(f"Faceit ID {playerID}")

    choice = int(input("Pick an option"))
    if choice == 1:
        getFaceitMatchHistory(playerID, amountOfGames, FaceitNickname, 'elo')
    if choice == 2:
        checkIfCached(playerID, amountOfGames, FaceitNickname, playerSteamID)
    if choice == 3:
        getFaceitMatchHistory(playerID, amountOfGames, FaceitNickname, 'stats')


def checkIfCached(playerID, amountOfGames, FaceitNickname, playerSteamID):
    if os.path.isfile(f"PlayerStats/{FaceitNickname}.csv") == True:
        print(f"{FaceitNickname}.csv exists")
        ti_c = os.path.getctime(f"PlayerStats/{FaceitNickname}.csv")
        choice = input(f"This data was created on {time.ctime(ti_c)}, are you sure you want to use it? y/n")

        if choice == "n":
            print("Generating new file and overwriting")
            ScrapeFaceitFinder(playerID, amountOfGames, FaceitNickname, playerSteamID)
        else:
            cachedDf = pd.read_csv(f"PlayerStats/{FaceitNickname}.csv")
            createGraph(cachedDf, FaceitNickname)
    else:
        print("False")
        ScrapeFaceitFinder(playerID, amountOfGames, FaceitNickname, playerSteamID)


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
    data.to_csv(f"PlayerStats/{FaceitNickname}.csv", index =False)
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


