# save_matches.py
#
# Takes in a Riot ID and Tag Line, retrieves the puuid, fetches recent match IDs, and saves match details to JSON files.

# Robust error handling and user prompts included.

import pathlib
import sys
import pandas as pd

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
from utilities.get_APIs import TftAPIClient

SAVE_PATH = BASE_DIR / "data" / "matches"
SAVE_PATH.mkdir(parents=True, exist_ok=True)

def save_matches(riot_id, tag_line, matchesNum):

    tftapi = TftAPIClient()

    puuid = tftapi.get_puuid_from_riot_id(riot_id, tag_line)
    matches = tftapi.get_matches_from_puuid(puuid, count=matchesNum)

    save_path = SAVE_PATH / f"{riot_id}#{tag_line}"
    save_path.mkdir(parents=True, exist_ok=True)

    for match in matches:
        if (save_path / f"match_{match}.json").exists():
            print(f"Match data for match ID: {match} already exists. Skipping download.")
            continue
        
        try:
            metadata, info = tftapi.get_match_details(match)
        except Exception as e:
            print(f"Error fetching details for match {match}: {e}")
            continue

        matchdata = {"metadata": metadata, "info": info}

        with open(save_path / f"match_{match}.json", "w") as f:
            import json
            json.dump(matchdata, f, indent=2)

        print(f"Saved match data for match ID: {match}")
    
def choice_menu():
    choice = -1
    while choice not in [1,2,3]:
        print(  "Menu:\n" \
                "  1: Save recent matches by Riot ID and Tag Line\n" \
                "  2: CSV File Input [riot_id, tagLine, matchesNum]\n" \
                "  3: Exit\n")
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    return choice

def main():
    
    choice = choice_menu()

    while choice != 3:
        if choice == 1:
            riot_id = input("Enter Riot ID: ")
            tag_line = input("Enter Tag Line: ")

            matchesNum = None
            while matchesNum is None or matchesNum < 0 or matchesNum > 100:
                try:
                    matchesNum = int(input("Enter number of recent matches to save: "))
                except ValueError:
                    print("Invalid number. Please enter an integer from 1 to 100.")
                    return
                
            save_matches(riot_id, tag_line, matchesNum)
            choice = choice_menu()
        elif choice == 2:
            file = input(   "=== Put file in /data folder (with .csv extension) ===\n" \
                            " File headers: riot_id, tag_line, matchesNum\n" \
                            " Please enter file name: "
                        )
            file = file + ".csv" if not file.endswith(".csv") else file
            for item in pathlib.Path(BASE_DIR/"data").iterdir():
                if item.name == file:
                    df = pd.read_csv(item, skipinitialspace=True)
                    df.columns = df.columns.str.strip()

                    for _, row in df.iterrows():
                        riot_id = str(row.get("riot_id", "")).strip()
                        tag_line = str(row.get("tag_line", "")).strip()
                        matches_num_raw = row.get("matchesNum", "")

                        if not riot_id or not tag_line:
                            print(f"Skipping row with missing riot_id/tag_line: {row.to_dict()}")
                            continue

                        try:
                            matches_num = int(matches_num_raw)
                        except (TypeError, ValueError):
                            print(f"Invalid matchesNum '{matches_num_raw}' for {riot_id}#{tag_line}; skipping.")
                            continue

                        save_matches(riot_id, tag_line, matches_num)
                    break
            break
    
    print("Exiting program...")

    
if __name__ == "__main__":
    main()
