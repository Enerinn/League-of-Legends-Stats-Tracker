import requests

api_key = "API_KEY"


def get_puuid(game_name, tag_line):
    game_name = game_name.replace(" ","%20")
    api_url = "https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"+game_name+"/"+tag_line
    x = requests.get(api_url, params = {"api_key": api_key})
    response = x.json()
    global puuid
    puuid = response["puuid"]
    return puuid

def get_match_id(puuid, start = 0, count = 20, type = None):
    start = str(start)
    count = str(count)
    api_url = "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/"+puuid+"/ids"
    if type is None:
        x = requests.get(api_url, params= {"start":start, "count":count, "api_key":api_key})
    else:
        x = requests.get(api_url, params= {"type": type, "start":start, "count":count, "api_key":api_key})
    response = x.json()
    return response

def get_match_info(match_id):
    api_url = "https://americas.api.riotgames.com/lol/match/v5/matches/"+match_id
    response = requests.get(api_url, params={"api_key": api_key}).json()
    return response

def get_participant_id(match_stats):
    index = match_stats["metadata"]["participants"].index(puuid)
    return index
    
def get_match_kda(match_stats):
    participant_id = get_participant_id(match_stats)#
    index = {"champion played": None, "kills": None, "deaths": None, "assists": None }
    index.update({"champion played": match_stats["info"]["participants"][participant_id]["championName"]})
    index.update({"kills": match_stats["info"]["participants"] [participant_id]["kills"]})
    index.update({"deaths": match_stats["info"]["participants"][participant_id]["deaths"]})
    index.update({"assists": match_stats["info"]["participants"][participant_id]["assists"]})
    return index
  
    
def get_match_outcome(match_stats):
    participant_id = get_participant_id(match_stats)
    index = {"champion played": None, "match result": None, "CS": None, "time": None}
    index.update({"champion played": match_stats["info"]["participants"][participant_id]["championName"]})
    index.update({"match result": match_stats["info"]["participants"][participant_id]["win"]})
    index.update({"CS": match_stats["info"]["participants"][participant_id]["totalMinionsKilled"]+match_stats["info"]["participants"][get_participant_id(match_stats)]["neutralMinionsKilled"]})
    index.update({"time": match_stats["info"]["participants"][participant_id]["timePlayed"]})

    for x,y in index.items():
        if x == "match result":
            if y == True:
                index.update({x: "Win"})
            else:
                index.update({x: "Lose"})
    return index

def get_winrate (all_match_outcome):
    winrate = 0
    for match in all_match_outcome:
        if match["match result"] == "Win":
            winrate = winrate+1
    winrate = winrate/len(all_match_outcome)*100
    print("winrate: %.2f" % winrate)
    
    
def get_match_history(match_id_list):
    all_kda = []
    all_match_outcome = []
    for match_id in match_id_list:
        match_stats = get_match_info(match_id)
        all_kda.append(get_match_kda(match_stats))
        all_match_outcome.append(get_match_outcome(match_stats))
    
    # the spacing may be off since it was originally designed to print in discord
    data = "```{:>8} {:>12} {:>12} {:>12} {:>16}```".format("Champion", "K/D/A", "Result", "CS", "Time\n")
    for i in range(len(all_match_outcome)):
        minutes, seconds = divmod(all_match_outcome[i]["time"], 60)
        kda = f"{all_kda[i]["kills"]}/{all_kda[i]["deaths"]}/{all_kda[i]["assists"]}"
        data += ("```{:>12} {:>12} {:>12} {:>12} {:>12.0f}:{:>02.0f} \n```".format(all_match_outcome[i]["champion played"], kda, all_match_outcome[i]["match result"], all_match_outcome[i]["CS"], minutes, seconds))
    return data