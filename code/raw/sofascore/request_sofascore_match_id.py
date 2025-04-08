import pandas as pd
import sys
from functions import get_json

def insert_data(league_id, season_id, round, slug="", playoff=False):
    """
    Fetches match data for a specific league, season, and round from a Sofascore API
    and appends it to a CSV file.

    Args:
        league_id (int): The ID of the league.
        season_id (int): The ID of the season.
        round (int or str): The round number or identifier.
        slug (str, optional): The slug for the round (used for playoff rounds). Defaults to "".
        playoff (bool, optional): A flag indicating if it's a playoff round. Defaults to False.
    """
    # Construct the API URL to get event (match) information based on whether it's a playoff.
    if playoff:
        # For playoff rounds, the API URL includes the round slug.
        id_response = get_json(f'https://www.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/events/round/{round}/slug/{slug}')
    else:
        # For regular rounds, the API URL only includes the round number.
        id_response = get_json(f'https://www.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/events/round/{round}')

    # Check if the API request for match IDs was successful (status code 200).
    if id_response["status_code"] == 200:
        # If the request was successful, extract the JSON data containing the event (match) information.
        data_id = id_response["json"]
        # Initialize an empty list to store the extracted match data as dictionaries.
        matchs = []
        # Iterate through each event (match) in the fetched data.
        for _ in data_id["events"]:
            # Create a dictionary to store relevant information for each match.
            match = {
                "id": _["id"],  # Unique identifier for the match.
                "tournament": _["tournament"]["slug"],  # Slug (short name) of the tournament.
                "match_name": f'{_["homeTeam"]["shortName"]}-{_["awayTeam"]["shortName"]}',  # Construct the match name from the short names of the home and away teams.
                "league": _["tournament"]["slug"],  # League slug (same as tournament slug in this context).
                "country": _["tournament"]["category"]["country"]["alpha3"],  # Alpha-3 code of the country where the league is based.
                "season": _["season"]["year"],  # Year of the season.
                "round": _["roundInfo"]["round"],  # The round number or identifier.
                "status": _["status"]["type"]  # The current status of the match (e.g., Finished, Live, Not Started).
            }
            # Append the created match dictionary to the list of matches.
            matchs.append(match)
            # Explicitly delete the 'match' variable to free up memory after appending (optional but good practice in loops).
            del match

        # Read the existing CSV file containing match data for the league and season.
        save_file = pd.read_csv(f"../../../data/raw/sofascore/id/matchs/{league_id}_{season_id}.csv")
        # Create a Pandas DataFrame from the list of extracted match data.
        data_to_save = pd.DataFrame(matchs)
        # Concatenate the existing DataFrame with the new DataFrame containing the fetched match data.
        save_file = pd.concat([save_file, data_to_save])
        # Save the updated DataFrame back to the same CSV file, overwriting the previous content (index=False prevents writing DataFrame index to the CSV).
        save_file.to_csv(f"../../../data/raw/sofascore/id/matchs/{league_id}_{season_id}.csv", index=False)
        # Explicitly delete the DataFrames to free up memory.
        del data_to_save, save_file
    else:
        # If the API request failed (status code is not 200), print an error message including the status code and the round number.
        print(f"error: {id_response['status_code']}, round: {round}")

def main(league_id, season_id):
    """
    Fetches round information for a specific league and season from a Sofascore API
    and potentially triggers data insertion for each round.

    Args:
        league_id (int): The ID of the league.
        season_id (int): The ID of the season.
    """
    # Initialize an empty Pandas DataFrame to store match information (though it's saved empty initially).
    save_file = pd.DataFrame(columns=["id", "tournament", "match_name", "league", "country", "season", "round", "status"])
    # Save the empty DataFrame to a CSV file in a specified directory.
    # The filename is constructed using the league and season IDs.
    save_file.to_csv(f"../../../data/raw/sofascore/id/matchs/{league_id}_{season_id}.csv", index=False)

    # Construct the API URL to retrieve round information for the given league and season.
    rounds_url = f"https://www.sofascore.com/api/v1/unique-tournament/{league_id}/season/{season_id}/rounds"
    # Call the get_json function (assumed to be defined elsewhere) to fetch data from the API.
    # This function is expected to return a dictionary with a 'status_code' and potentially 'json' data.
    rounds = get_json(rounds_url)

    # Check if the API request was successful by examining the 'status_code'.
    if rounds["status_code"] == 200:
        # If the status code is 200 (OK), it means the API request was successful.
        # Extract the JSON data containing the round information.
        data_rounds = rounds["json"]
        # Iterate through each item in the "rounds" list within the fetched JSON data.
        for _ in data_rounds["rounds"]:
            # Check the length of the current round information item.
            # The structure of the items in the "rounds" list might vary.
            if len(_) > 1:
                # If the length of the item is greater than 1, it likely contains more detailed information.
                # Call the insert_data function (assumed to be defined elsewhere) to process this round's data.
                # It passes the league ID, season ID, the 'round' number, a 'slug' (likely a unique identifier), and True.
                insert_data(league_id, season_id, _["round"], _["slug"], True)
            else:
                # If the length of the item is not greater than 1, it might contain less detailed information.
                # Call the insert_data function with fewer parameters.
                # It passes the league ID, season ID, and the 'round' number.
                insert_data(league_id, season_id, _["round"])
            # Print "ok" after processing each round, likely for logging or simple progress tracking.
            print("ok")
    else:
        # If the 'status_code' is not 200, it indicates an error during the API request.
        print("error")

if __name__ == "__main__":
    # Check if the number of command-line arguments is not equal to 3.
    # sys.argv is a list containing the script name and the arguments passed to it.
    # We expect the script name (index 0), league_id (index 1), and season_id (index 2).
    if len(sys.argv) != 3:
        # If the number of arguments is incorrect, print a usage message to the user
        # explaining how to run the script correctly.
        print("Usage: python run.py <league_id> <season_id>")
        # Exit the script with a non-zero exit code (typically 1) to indicate an error.
        sys.exit(1)

    # If the correct number of arguments is provided, proceed to extract them.
    # The league ID is the second argument passed to the script (at index 1).
    league_id = sys.argv[1]
    # The season ID is the third argument passed to the script (at index 2).
    season_id = sys.argv[2]

    # Call the 'main' function (assumed to be defined elsewhere in the script or imported)
    # with the extracted league ID and season ID as arguments.
    main(league_id, season_id)