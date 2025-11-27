# APIs.py

"""
Wrapper for Riot Games APIs

This module contains functions to interact with the Riot Games API to retrieve player and match information for Teamfight Tactics (TFT).

"""

import os
import requests
import dotenv
import time

dotenv.load_dotenv()
wait = 120  # wait time between requests in seconds to avoid rate limiting

class RiotAPIError(RuntimeError):
    """Raised when the Riot API returns a non-200 response."""

    def __init__(self, status_code: int, message: str, url: str):
        super().__init__(f"Riot API error {status_code} for {url}: {message}")
        self.status_code = status_code
        self.url = url
        self.message = message

    def wait_before_retry(self, wait_time: int):
        """Wait for a specified time before retrying the request."""
        print(f"Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)


class TftAPIClient:
    def __init__(self):
        self.api_key = os.getenv("X-RIOT-TOKEN")
        if not self.api_key:
            raise ValueError("API key is missing. Provide a valid Riot Games API key.")

        self.region = "americas"
        self.base_url = f"https://{self.region}.api.riotgames.com"
        self.headers = {"X-RIOT-TOKEN": self.api_key}

    def _get_with_rate_limit(self, url: str, params: dict | None = None):
        """Perform a GET, waiting on 429."""
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 429:
            RiotAPIError(response.status_code, "Rate limit exceeded", url).wait_before_retry(wait)
            response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise RiotAPIError(response.status_code, response.text, url)

        return response

    def get_puuid_from_riot_id(self, gameName: str, tagLine: str) -> str:
        """
        Docstring for get_puuid_from_riot_id
        
            :param gameName: First part of Riot ID
            :param tagLine: Second part of Riot ID

        Returns: 
            puuid (str)
        """
        # ACCOUNT-V1
        url = self.base_url+f"/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"

        # Parse GET request response
        response = self._get_with_rate_limit(url)

        AccountDto = response.json()
        return AccountDto["puuid"]


    def get_matches_from_puuid(self, puuid: str, count:int=20, start:int=0) -> list:
        """
        Docstring for get_matches_from_puuid
        
        :param puuid: puuid of the player

        Returns: 
            matchList (list)
        """
        # TFT-MATCH-V1
        url = self.base_url+f"/tft/match/v1/matches/by-puuid/{puuid}/ids"

        params = {
            "count": count,
            "start": start,
        }

        response = self._get_with_rate_limit(url, params=params)

        matchList = response.json()

        return matchList


    def get_match_details(self, matchId: str) -> tuple[dict, dict]:
        """
        Docstring for get_match_details
        
        :param matchId: string match ID

        Returns: 
            metadata (dict), info (dict)
        """
        # TFT-MATCH-V1
        url = self.base_url+f"/tft/match/v1/matches/{matchId}"

        response = self._get_with_rate_limit(url)

        matchDetails = response.json()

        return matchDetails["metadata"], matchDetails["info"]
    
