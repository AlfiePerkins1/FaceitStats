import os
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt

import config


def getFaceitID():
    #Gets the player's faceit ID from their faceit nickname

    payload = {}
    headers = {
        'Authorization': config.api_key,
    }

    FaceitNickname = input("Enter faceit nickname")

    # Getting faceit ID
    URL = f"https://open.faceit.com/data/v4/players?nickname={FaceitNickname}&game=csgo="

    response = requests.request("GET", URL, headers=headers, data=payload)
    data = response.json()
    playerID = data['player_id']
    playerSteamID = data['steam_id_64']
    return playerID, FaceitNickname, playerSteamID

def getFaceitMatchHistory(faceitID):

    limit = int(input("How many games would you like to search?"))

    matchID = []
    offset = 0
    maxSearch = 0
    loopIndex = limit / 100
    i = 0
    payload = {}
    headers = {
        'Authorization': config.api_key,
    }
    # Limit of 100 games per request

    if (limit > 100):
        maxSearch = 100
    else:
        maxSearch = limit

    while i < loopIndex:
        # Getting match history
        URL = f"https://open.faceit.com/data/v4/players/{faceitID}/history?game=csgo&offset={offset}&limit={maxSearch}"

        response = requests.request("GET", URL, headers=headers, data=payload)
        data = response.json()

       # print(data['items'][0]['match_id'])

        x = 0
        for x in range(maxSearch):
            matchID.append(data['items'][x]['match_id'])
            print(matchID[x])

        offset += 100
        time.sleep(2)
        i += 1

    return matchID, limit

def checkIfCached(faceitNickname):
    if os.path.isfile(f"PlayerStats/{faceitNickname}.csv") == True:
        data = pd.read_csv(f"PlayerStats/{faceitNickname}.csv")
        print(f"{faceitNickname}.csv exists in PlayerStats folder, with {len(data)} games")
        ti_c = os.path.getctime(f"PlayerStats/{faceitNickname}.csv")
        choice = input(f"This data was created on {time.ctime(ti_c)}, are you sure you want to use it? y/n")

        if choice == "n":
            return False
        else:
            return True
    else:
        return False

def scrapeFaceitFinder(faceitNickname, steamID, limit):
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    url = f"https://faceitfinder.com/stats/{steamID}/matches/1"
    response = requests.get(url, headers=HEADERS)
    print(response)

    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', class_='matches_table')
    # print(table)

    headers = []

    for i in table.find_all('th'):
        title = i.text
        headers.append(title)
        # print(title)

    scrapedData = pd.DataFrame(columns=headers)

    # First page
    for j in table.find_all('tr')[1:]:
        row_data = j.find_all('td')
        row = [i.text for i in row_data]
        length = len(scrapedData)
        scrapedData.loc[length] = row

    # print(scrapedData)

    # Get match number
    gameNum = int(scrapedData.iloc[0, 0])
    numOfPages = int(gameNum / 20) + 1

    for i in range(numOfPages):
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

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

    scrapedData["#"] = scrapedData["#"].astype('int')
    scrapedData.sort_values(['#'], inplace=True)

    data = scrapedData[scrapedData.ELO != "—"]

    data['ELO'] = data['ELO'].str.replace(r'\([^()]*\)', '', regex=True)

    data['ELO'] = pd.to_numeric(data['ELO'])

    # Split Data to how many games
    data = data.iloc[:limit]
    print(data)
    data.to_csv(f"PlayerStats/{faceitNickname}.csv", index=False)
    return data

def getFaceitMatchStats(faceitNickname, matchIDArray,limit):
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


    for x in range(limit):
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

        # Find player ID
        i = 0
        playerNum = 0
        playerTeam = 0
        for i in range(5):
            try:
                if StatsData['rounds'][0]['teams'][1]['players'][i]['nickname'] == faceitNickname:
                    playerNum = i
                    playerTeam = 1
                    print(f"Found, playerID of {i} team 1")
                elif StatsData['rounds'][0]['teams'][0]['players'][i]['nickname'] == faceitNickname:
                    playerNum = i
                    playerTeam = 0
                    print(f"Found, playerID of {i} team 0")
                else:
                    pass
                i += 1
            except:
                # Occurs when a player left the game
                ("Only 4 players on team")

        # Check to see if the game is a hub
        if data['competition_type'] == "hub":
            print(f"Game {x} is a hub game, no average elo")
        else:
            try:
                # Loop through players from Team 1
                Team1Names = []
                while j in range(5):
                    Team1Names.append(data['teams']['faction1']['roster'][j]['nickname'])
                    j += 1
                if faceitNickname in Team1Names:
                    try:
                        myTeam.append(True)
                        EnemyElo.append(data['teams']['faction2']['stats']['rating'])

                        myElo.append(data['teams']['faction1']['stats']['rating'])

                        # Add stats here
                        KD = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "K/D Ratio"]
                        KR = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "K/R Ratio"]
                        HSP = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "Headshots %"]
                        Kills = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "Kills"]
                        myKD.append(KD)
                        myKR.append(KR)
                        myHSP.append(HSP)
                        myKills.append(Kills)
                        print(
                            f"Appended for game ID {matchIDArray[j]}, KD: {KD}, KR: {KR}, HSP: {HSP}, Kills: {Kills} ")

                    except:
                        print("No average elo")
                else:
                    try:
                        myTeam.append(False)
                        EnemyElo.append(data['teams']['faction1']['stats']['rating'])

                        myElo.append(data['teams']['faction2']['stats']['rating'])

                        # Add stats here
                        KD = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "K/D Ratio"]
                        KR = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "K/R Ratio"]
                        HSP = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "Headshots %"]
                        Kills = StatsData['rounds'][0]['teams'][playerTeam]['players'][playerNum]['player_stats'][
                            "Kills"]
                        myKD.append(KD)
                        myKR.append(KR)
                        myHSP.append(HSP)
                        myKills.append(Kills)
                        print(
                            f"Appended for game ID {matchIDArray[j]}, KD: {KD}, KR: {KR}, HSP: {HSP}, Kills: {Kills} ")

                        # print(f"Elo for my team {myElo[x]}")
                    except:
                        print("No average elo")

            except:
                print("Player not found")

    statsToSave = pd.DataFrame(
        {
            'Enemy Elo': EnemyElo,
            'My Team Elo': myElo,
            'My KD': myKD,
            'My KR': myKR,
            'My Headshot': myHSP,
            'My Kills': myKills

        }
    )
    statsToSave.to_csv(f"PlayerStats/{faceitNickname}.csv", index=False)
    return statsToSave

def menu():


    print("1. Elo throughout time graph")
    print("2. KD compared to Enemey Elo")
    print("3. Enemy Elo compared to own Elo")
    choice = int(input("What would you like to do with the data?"))
    return choice

def kdEloGraph(faceitAPIData, faceitNickname):
    plt.scatter(faceitAPIData['Enemy Elo'], faceitAPIData['My KD'], color='r')
    plt.xlabel("Enemy Elo")
    plt.ylabel("KD")
    plt.title(f"Elo compared with KD for {faceitNickname}")
    plt.grid()
    plt.plot()
    plt.show()


if __name__ == "__main__":

    #Only need the FaceitFinderAPI to plot the average Elo graphs, faceitAPI can be done for everything else

    faceitID, faceitNickname, playerSteamID = getFaceitID()
    matchIDArray, limit = getFaceitMatchHistory(faceitID)
    useCached = checkIfCached(faceitNickname)

    if useCached == True:
        #They want to use the data stored
        #faceitFinderData = pd.read_csv(f"PlayerStats/{faceitNickname}.csv")
        faceitAPIData = pd.read_csv(f"PlayerStats/{faceitNickname}.csv")
    else:
        #They want to generate new data
        #Scrape from faceit finder (for game stats) and from faceitAPI for average Elo then combine
        #faceitFinderData = scrapeFaceitFinder(faceitNickname, playerSteamID, limit)
        faceitAPIData = getFaceitMatchStats(faceitNickname,matchIDArray, limit)

    choice = menu()
    if choice == 1:
        #Plot Elo Through Time Graph using faceitFinderData
        pass
    elif choice == 2:
        #PlotKD compared to enemy elo using faceitAPIData
        #print(faceitAPIData)
        kdEloGraph(faceitAPIData, faceitNickname)
    elif choice  ==3:
        #Plot enemy elo compared to team elo using faceitAPIData
        pass
