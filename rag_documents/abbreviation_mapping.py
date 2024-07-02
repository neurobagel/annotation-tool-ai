import pandas as pd
from bs4 import BeautifulSoup
import requests  # type: ignore
import json
from nltk.tokenize import word_tokenize
from typing import List, Dict, Set
from nltk.corpus import wordnet as wn


def extract_terms_from_web() -> None:
    # Define the URL you want to scrape from
    url: str = (
        "https://en.wikipedia.org/wiki/\
            List_of_abbreviations_for_diseases_and_disorders"
    )

    # Make a GET request to fetch the raw HTML content
    response = requests.get(url)

    # Use the response with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Continue with your existing code...

    # Find the tables containing the abbreviations
    tables: List[BeautifulSoup] = soup.find_all(
        "table", {"class": "wikitable"}
    )

    # Initialize an empty list to store DataFrames
    dfs: List[pd.DataFrame] = []

    for table in tables:
        # Extract headers
        headers: List[str] = [
            header.text.strip() for header in table.find_all("th")
        ]
        # Extract rows, skipping the header row
        rows: List[BeautifulSoup] = table.find_all("tr")[1:]

        # Initialize an empty list to store the cleaned data rows
        cleaned_data: List[List[str]] = []

        for row in rows:
            # Extract data cells from the row
            cells: List[str] = [
                cell.text.strip() for cell in row.find_all(["td", "th"])
            ]

            # If the row has fewer cells than headers, pad it with None values
            while len(cells) < len(headers):
                cells.append("")

            # If the row has more cells than headers, trim the excess cells
            if len(cells) > len(headers):
                cells = cells[: len(headers)]

            cleaned_data.append(cells)

        # Create a DataFrame for the current table with the cleaned data
        df: pd.DataFrame = pd.DataFrame(cleaned_data, columns=headers)
        # Append the DataFrame to the list
        dfs.append(df)

    # Concatenate all DataFrames
    final_df: pd.DataFrame = pd.concat(dfs, ignore_index=True)

    # Save to CSV and TSV
    # final_df.to_csv('medical_abbreviations.csv', index=False)
    final_df.to_csv(
        "rag_documents/medical_abbreviations.tsv", index=False, sep="\t"
    )

    print("Data has been saved to 'medical_abbreviations.tsv'")


def find_synonyms(word: str) -> Set[str]:
    synonyms: Set[str] = set()
    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms


def find_similar_phrases(
    list1: List[str], list2: List[str]
) -> Dict[str, List[str]]:
    similar_phrases_map: Dict[str, List[str]] = {}
    for phrase1 in list1:
        phrase1_words: Set[str] = set(word_tokenize(phrase1.lower()))
        synonyms1: Dict[str, Set[str]] = {
            word: find_synonyms(word) for word in phrase1_words
        }

        for phrase2 in list2:
            phrase2_words: Set[str] = set(word_tokenize(phrase2.lower()))

            # Check similarity
            if all(
                any(
                    word2 in synonyms or word2 == word1
                    for word1, synonyms in synonyms1.items()
                )
                for word2 in phrase2_words
            ):
                if phrase1 not in similar_phrases_map:
                    similar_phrases_map[phrase1] = [phrase2]
                elif phrase2 not in similar_phrases_map[phrase1]:
                    similar_phrases_map[phrase1].append(phrase2)
    return similar_phrases_map


def create_json_file(
    similar_words_map: Dict[str, List[str]],
    abbreviations_df: pd.DataFrame,
    output_file: str,
) -> None:
    json_list: List[Dict[str, str]] = []
    for phrase1, similar_phrases in similar_words_map.items():
        abbreviation: str = abbreviations_df[
            abbreviations_df.iloc[:, 1] == phrase1
        ].iloc[0, 0]
        for label in similar_phrases:
            json_list.append({"abbreviation": abbreviation, "label": label})

    with open(output_file, "w") as file:
        json.dump(json_list, file, indent=4)


def main() -> None:
    extract_terms_from_web()

    # Load the medical abbreviations from the TSV file
    abbreviations_df: pd.DataFrame = pd.read_csv(
        "rag_documents/medical_abbreviations.tsv", sep="\t"
    )
    # Get matching columns
    list1: List[str] = abbreviations_df.iloc[:, 1].tolist()

    # Load the diagnosis terms from the JSON file
    with open("app/parsing/diagnosisTerms.json") as file:
        data: List[Dict[str, str]] = json.load(file)

    # Extract the label entries from the data
    list2: List[str] = [entry["label"] for entry in data]

    similar_words_map: Dict[str, List[str]] = find_similar_phrases(
        list1, list2
    )
    for phrase1, similar_phrases in similar_words_map.items():
        print(f"Words from list1 '{phrase1}':")
        for phrase2 in similar_phrases:
            print(f" - Found in list2: '{phrase2}'")

    # Create JSON file with abbreviation-label pairs
    create_json_file(
        similar_words_map,
        abbreviations_df,
        "rag_documents/abbreviation_label_pairs.json",
    )


if __name__ == "__main__":
    main()
