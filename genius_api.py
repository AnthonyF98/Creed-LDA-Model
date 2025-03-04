import os
import requests
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load API Key from .env file
load_dotenv()
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

BASE_URL = "https://api.genius.com"
ARTIST_ID = 13217  # Creed's Genius Artist ID

# Function to get all songs by Creed using Genius API
def get_all_creed_songs():
    headers = {"Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"}
    songs = []
    page = 1

    while True:
        url = f"{BASE_URL}/artists/{ARTIST_ID}/songs"
        params = {"per_page": 50, "page": page, "sort": "title"}  # Fetch 50 songs per page
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print("❌ Error fetching songs")
            break

        data = response.json().get("response", {}).get("songs", [])
        if not data:
            break  # Stop if no more results

        for song in data:
            song_id = song["id"]
            song_title = song["title"]
            song_url = get_song_url(song_id)  # Fetch official song URL
            songs.append((song_title, song_url))

        page += 1  # Move to the next page

        # Stop once we have all 126 songs
        if len(songs) >= 126:
            break

    return songs[:126]

# Function to get the official song URL from Genius API
def get_song_url(song_id):
    headers = {"Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"}
    url = f"{BASE_URL}/songs/{song_id}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None  # Return None if request fails

    return response.json().get("response", {}).get("song", {}).get("url")

# Function to scrape lyrics from a song page
def get_lyrics(song_url):
    if not song_url:
        return "❌ No URL found for this song."

    headers = {"User-Agent": "Mozilla/5.0"}  # Prevent bot blocking
    response = requests.get(song_url, headers=headers)

    if response.status_code != 200:
        return "❌ Error loading song page."

    soup = BeautifulSoup(response.text, "html.parser")

    # New Genius lyric structure (2024)
    lyrics_divs = soup.select("div[data-lyrics-container='true']")
    
    if not lyrics_divs:
        return "Lyrics not found."

    lyrics = "\n".join([div.get_text("\n") for div in lyrics_divs])
    return lyrics.strip() if lyrics else "Lyrics not found."


# Scrape all Creed songs and save lyrics
def scrape_creed_lyrics():
    songs = get_all_creed_songs()

    if not songs:
        print("❌ No songs found!")
        return

    filename = "Creed_lyrics.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for idx, (title, url) in enumerate(songs, start=1):
            print(f"🎵 Scraping [{idx}/{len(songs)}]: {title}")
            lyrics = get_lyrics(url)
            file.write(f"{title}\n\n{lyrics}\n\n{'='*40}\n\n")
            time.sleep(1)  # Prevents blocking

    print(f"\n✅ Lyrics saved to {filename}!")

# Run the script
scrape_creed_lyrics()


# python genius_api.py