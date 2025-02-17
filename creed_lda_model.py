import os
import re
import pandas as pd

############################################
############################################
######Converting into a data frame##########
############################################
############################################



# File Path
file_path = "Creed_lyrics.txt"

# Read file content
with open(file_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Helper function to clean song titles (remove "Live", "Remastered", etc.)
def clean_title(title):
    return re.sub(r"\(.*?\)", "", title, flags=re.IGNORECASE).strip()

# Process the lyrics file into structured format
songs = []
current_song = {"title": None, "version": None, "lyrics": ""}
reading_lyrics = False

for line in lines:
    line = line.strip()

    # If we hit a separator (======), the next line is the song title
    if line.startswith("="):
        if current_song["title"]:  # Save previous song before starting a new one
            songs.append(current_song)
        current_song = {"title": None, "version": None, "lyrics": ""}
        reading_lyrics = False  # Reset

    elif not current_song["title"]:  
        # First non-separator line after "======" is the song title
        current_song["title"] = clean_title(line)
        current_song["version"] = "Original" if "(" not in line else re.search(r"\((.*?)\)", line).group(1)

    else:
        # Append lyrics to the current song
        current_song["lyrics"] += line + "\n"
        reading_lyrics = True

# Append last song if not already saved
if current_song["title"] and reading_lyrics:
    songs.append(current_song)

# Convert to DataFrame
df = pd.DataFrame(songs)

# Save as CSV
csv_path = "Creed_Lyrics_Cleaned.csv"
df.to_csv(csv_path, index=False, encoding="utf-8")

import ace_tools as tools
tools.display_dataframe_to_user(name="Structured Creed Lyrics", dataframe=df)


############################################
############################################
######Cleaning the data frame###############
############################################
############################################


# Ensure "Original" versions are prioritized when removing duplicates
def keep_original_versions(df):
    # Sort so "Original" appears first
    df_sorted = df.sort_values(by="version", key=lambda x: x != "Original")
    # Drop duplicates, keeping the first occurrence (which will be "Original" if available)
    df_deduplicated = df_sorted.drop_duplicates(subset=["title"], keep="first")
    return df_deduplicated

# Apply function to clean the dataset
df_cleaned_final = keep_original_versions(df)

# Sort alphabetically by song title
df_cleaned_final_sorted = df_cleaned_final.sort_values(by="title")

# Save as CSV
csv_path = "Creed_Lyrics_Sorted.csv"
df_cleaned_final_sorted.to_csv(csv_path, index=False, encoding="utf-8")


############################################
############################################
######LDA Modeling on the Lyrics############
############################################
############################################
