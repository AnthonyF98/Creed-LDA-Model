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

import re
import pandas as pd
import gensim
from gensim import corpora
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk

def clean_lyrics(text):
    """
    Cleans song lyrics by removing section headers (e.g., [Verse 1], [Chorus]),
    filtering out common stopwords, and performing lemmatization.
    """
    section_pattern = r"\[.*?\]"  # Matches [Verse 1], [Chorus], etc.
    basic_stopwords = {
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves",
        "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
        "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was",
        "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and",
        "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between",
        "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on",
        "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
        "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
        "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
    }
    
    if pd.isna(text):
        return ""
    
    text = re.sub(section_pattern, "", text)  # Remove section headers
    words = word_tokenize(text.lower())  # Tokenize text
    words = [word for word in words if word.isalnum() and word not in basic_stopwords]  # Remove stopwords and punctuation
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]  # Lemmatization
    
    return " ".join(words)

def process_lyrics_csv():
    """
    Reads the 'Creed_Lyrics_Sorted.csv' file, cleans the lyrics column, and saves the processed data.
    """
    input_file = "Creed_Lyrics_Sorted.csv"
    output_file = "Cleaned_Lyrics.csv"
    df = pd.read_csv(input_file)
    df["cleaned_lyrics"] = df["lyrics"].apply(clean_lyrics)
    df.to_csv(output_file, index=False)
    print(f"Processed file saved to {output_file}")

def prepare_lda_model():
    """
    Prepares the dataset for LDA modeling.
    """
    df = pd.read_csv("Cleaned_Lyrics.csv")
    text_data = [doc.split() for doc in df["cleaned_lyrics"].dropna()]
    dictionary = corpora.Dictionary(text_data)
    corpus = [dictionary.doc2bow(text) for text in text_data]
    return dictionary, corpus, text_data

def run_lda_model(num_topics=10, num_words=15):
    """
    Runs an LDA model with the specified number of topics and words per topic.
    """
    dictionary, corpus, text_data = prepare_lda_model()
    lda_model = gensim.models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=10)
    topics = lda_model.print_topics(num_words=num_words)
    for topic in topics:
        print(topic)
    return lda_model

# Example: Run the function
if __name__ == "__main__":
    process_lyrics_csv()
    run_lda_model()

import re

# LDA topic output
lda_topics = [
    '0.059*"let" + 0.043*"go" + 0.022*"inside" + 0.021*"place" + 0.020*"change" + 0.019*"take" + 0.016*"higher" + 0.016*"u" + 0.015*"think" + 0.015*"make" + 0.013*"stay" + 0.013*"away" + 0.013*"peace" + 0.012*"know" + 0.012*"see"',
    '0.025*"see" + 0.020*"rain" + 0.019*"ca" + 0.018*"truth" + 0.017*"come" + 0.017*"sign" + 0.016*"head" + 0.014*"face" + 0.014*"look" + 0.014*"feel" + 0.012*"stay" + 0.012*"day" + 0.011*"like" + 0.011*"u" + 0.011*"tell"',
    '0.034*"sing" + 0.031*"one" + 0.026*"feel" + 0.024*"let" + 0.022*"yeah" + 0.019*"song" + 0.013*"change" + 0.012*"reason" + 0.012*"hide" + 0.012*"like" + 0.011*"never" + 0.011*"oh" + 0.011*"world" + 0.010*"stand" + 0.010*"get"',
    '0.027*"life" + 0.025*"wide" + 0.025*"open" + 0.022*"arm" + 0.021*"one" + 0.021*"oh" + 0.018*"eye" + 0.017*"yeah" + 0.016*"ready" + 0.014*"freedom" + 0.014*"everything" + 0.014*"show" + 0.014*"dime" + 0.010*"allusion" + 0.010*"take"',
    '0.033*"zone" + 0.031*"jesus" + 0.022*"time" + 0.020*"suddenly" + 0.019*"roll" + 0.017*"yeah" + 0.016*"got" + 0.016*"wo" + 0.014*"mine" + 0.013*"stand" + 0.011*"lord" + 0.010*"friend" + 0.010*"bound" + 0.010*"tied" + 0.010*"man"',
    '0.026*"tell" + 0.019*"america" + 0.018*"fly" + 0.017*"going" + 0.013*"na" + 0.012*"gon" + 0.010*"right" + 0.010*"rise" + 0.010*"know" + 0.009*"yeah" + 0.009*"time" + 0.009*"hurt" + 0.009*"aslan" + 0.009*"asla" + 0.009*"ekip"',
    '0.061*"fight" + 0.038*"say" + 0.033*"know" + 0.028*"back" + 0.027*"little" + 0.023*"good" + 0.022*"get" + 0.020*"eighteen" + 0.018*"keep" + 0.017*"sister" + 0.017*"wrong" + 0.015*"fighting" + 0.012*"like" + 0.010*"girl" + 0.010*"looked"',
    '0.082*"foot" + 0.066*"pant" + 0.039*"like" + 0.035*"around" + 0.029*"u" + 0.028*"friend" + 0.026*"end" + 0.023*"love" + 0.016*"gone" + 0.015*"six" + 0.012*"eye" + 0.012*"say" + 0.010*"far" + 0.009*"hold" + 0.009*"let"',
    '0.019*"reach" + 0.016*"one" + 0.016*"ca" + 0.015*"time" + 0.014*"overcome" + 0.013*"soul" + 0.013*"listen" + 0.013*"give" + 0.012*"learn" + 0.012*"head" + 0.010*"held" + 0.009*"entitled" + 0.009*"circle" + 0.009*"pain" + 0.009*"full"',
    '0.070*"yeah" + 0.038*"give" + 0.036*"away" + 0.031*"love" + 0.024*"wash" + 0.024*"year" + 0.017*"sent" + 0.017*"eye" + 0.017*"stripped" + 0.016*"tear" + 0.015*"hope" + 0.014*"well" + 0.014*"beautiful" + 0.013*"everything" + 0.013*"hide"'
]


# Extract words inside quotes
extracted_words = [re.findall(r'"(.*?)"', topic) for topic in lda_topics]

# Convert to a structured dictionary
lda_word_dict = {f"Topic {i}": words for i, words in enumerate(extracted_words)}

# Display the extracted words
import pandas as pd

df_words = pd.DataFrame.from_dict(lda_word_dict, orient='index').transpose()

print(df_words)



import pandas as pd

# Define religious terms
religious_terms = {
    "jesus", "god", "christ", "faith", "pray", "prayer", "bible", "church", "heaven", "grace",
    "gospel", "salvation", "holy", "spirit", "lord", "redeem", "forgive", "sin", "believe", "worship",
    "glory", "cross", "crucify", "messiah", "hallelujah", "praise", "blessing", "miracle", "sacred", "eternal",
    "trinity", "disciple", "apostle", "covenant", "resurrection", "righteous", "commandments", "truth", "mercy",
    "light", "love", "peace", "prophet", "kingdom", "charity", "repent", "shepherd", "sacrifice", "revival", "deliverance"
}

# Ensure df_words exists (df_words should be a Pandas DataFrame)
if "df_words" in locals() or "df_words" in globals():  # Check if df_words exists
    religious_counts = {}

    # Iterate through each topic (columns) in df_words
    for topic in df_words.columns:
        words = df_words[topic].dropna().tolist()  # Get words from the topic, drop NaNs

        # Find religious words in the topic
        religious_matches = [word for word in words if word in religious_terms]

        # Store analysis
        religious_counts[topic] = {
            "Total Words": len(words),
            "Religious Words": len(religious_matches),
            "Religious Percentage": round((len(religious_matches) / len(words)) * 100, 2) if len(words) > 0 else 0,
            "Matched Words": religious_matches
        }

    # Convert to DataFrame
    df_religious_analysis = pd.DataFrame.from_dict(religious_counts, orient="index")

    # Print or display results
    print(df_religious_analysis)

else:
    print("Error: df_words does not exist. Ensure df_words is loaded before running this analysis.")
