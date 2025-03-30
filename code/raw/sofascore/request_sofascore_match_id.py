import requests
import json
import pandas as pd
import sys

def insert_data(league_id, season_id, round, slug="", playoff=False):
    if playoff:
        id_response = requests.get(f'https://www.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/events/round/{round}/slug/{slug}')
    else:
        id_response = requests.get(f'https://www.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/events/round/{round}')
    
    if id_response.status_code == 200:
        data_id = id_response.json()
        matchs = []
        for _ in data_id["events"]:
            match = {
                "id" : _["id"],
                "tournament": _["tournament"]["slug"],
                "match_name": f'{_["homeTeam"]["shortName"]}-{_["awayTeam"]["shortName"]}',
                "league": _["tournament"]["slug"],
                "country": _["tournament"]["category"]["country"]["alpha3"],
                "season": _["season"]["year"],
                "round": _["roundInfo"]["round"],
                "status": _["status"]["type"]
            }
            matchs.append(match)
            del match
        
        save_file = pd.read_csv(f"../../../data/raw/sofascore/id/matchs/{league_id}_{season_id}.csv") 
        data_to_save = pd.DataFrame(matchs)
        save_file = pd.concat([save_file, data_to_save])
        save_file.to_csv(f"../../../data/raw/sofascore/id/matchs/{league_id}_{season_id}.csv", index=False)
        del data_to_save, save_file
    else:
        print(f"error: {id_response.status_code}, round: {_['round']}")


def main(league_id, season_id):
    save_file = pd.DataFrame(columns=["id", "tournament", "match_name", "league", "country", "season", "round", "status"])
    save_file.to_csv(f"../../../data/raw/sofascore/id/matchs/{league_id}_{season_id}.csv", index=False)
    rounds = requests.get(f"https://www.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/rounds")
    if rounds.status_code == 200:
        data_rounds = rounds.json()
        for _ in data_rounds["rounds"]:
            if len(_) > 1:
                insert_data(league_id, season_id, _["round"], _["slug"], True)
            else:
                insert_data(league_id, season_id, _["round"])
    else:
        print("error")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run.py <league_id> <season_id>")
        sys.exit(1)

    league_id = sys.argv[1]
    season_id = sys.argv[2]

    main(league_id, season_id)

