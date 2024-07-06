import json
from typing import List
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re


def get_diagnosis_labels() -> List[str]:
    with open("app/parsing/diagnosisTerms.json", "r") as file:
        diagnosis_terms = json.load(file)
    diagnosis_labels = []
    diagnosis_labels = [term["label"] for term in diagnosis_terms]
    return diagnosis_labels


if __name__ == "__main__":

    # Prepare .tsv file
    diagnosisTerms = get_diagnosis_labels()
    # print(diagnosisTerms)

    # initialize model - llama3 run locally
    llm = ChatOllama(model="llama3")

    prompt = PromptTemplate(
        template="""Please respond abbreviations most commonly used for the
following term: {term}.
Give only the abbreviations as output and prefer the ones used in research
data and papers.
For example:
Input:'diabetes mellitus'
Output:'DM', 'DM2', 'DM1'.
Do Not Give any explanation in the output.
Input: "{term}"
Output= <abbreviations>

    """,
        input_variables=["term"],
    )

    # create chain
    chain = prompt | llm

    for term in diagnosisTerms:
        print(term)
        response = chain.invoke({"term": term})

        print(response)
        response = str(response)

        # Extract the content part using regular expressions
        match = re.search(r"content='(.*?)'", response)
        if match:
            content_part = match.group(1)
        else:
            print("No content part found in response.")
            content_part = ""

        # Step 2: Split the content
        abbreviations_list = (
            [abbr.strip() for abbr in content_part.split(",")]
            if content_part
            else []
        )

        # Step 3: Create a dictionary with the desired structure
        result_dict = {"label": term, "abbreviations": abbreviations_list}

        # Check if any abbreviations were found
        if not abbreviations_list:
            print("No abbreviations found for term:", term)
            continue  # Skip to the next term if no abbreviations were found

        # Append result_dict to the JSON file
        with open("rag_documents/abbreviationsDiagnosis.json", "r+") as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = []

            existing_terms = [item["label"] for item in data]
            # Assuming further processing continues from here...
            if term in existing_terms:
                for item in data:
                    if item["label"] == term:
                        existing_abbreviations = item["abbreviations"]
                        new_abbreviations = list(
                            set(existing_abbreviations + abbreviations_list)
                        )
                        item["abbreviations"] = new_abbreviations
                        break
            else:
                data.append(result_dict)

            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
            file.write("\n")

        # Now result_dict contains the structured data
        print(result_dict)

        # Append result_dict to the JSON file
        with open(
            "rag_documents/abbreviationsDiagnosis.json",
            "r+",
        ) as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = []

            existing_terms = [item["label"] for item in data]
            if term in existing_terms:
                for item in data:
                    if item["label"] == term:
                        existing_abbreviations = item["abbreviations"]
                        new_abbreviations = list(
                            set(existing_abbreviations + abbreviations_list)
                        )
                        item["abbreviations"] = new_abbreviations
                        break
            else:
                data.append(result_dict)

            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
            file.write("\n")


# Load the JSON data from the file
with open(
    "rag_documents/abbreviationsDiagnosis.json", "r", encoding="utf-8"
) as file:
    data = json.load(file)

# Create a PDF file to write the output
c = canvas.Canvas("abbreviations.pdf", pagesize=letter)
width, height = letter  # Get the width and height of the page
line_height = 14  # Define the line height
current_height = height - 50  # Start 50 pixels down from the top

# Iterate through each entry in the JSON data
for entry in data:
    label = entry["label"]
    for abbreviation in entry["abbreviations"]:
        line = f"{abbreviation}: {label}"
        # Write each line to the PDF file
        c.drawString(50, current_height, line)
        current_height -= line_height
        # Check if we need to start a new page
        if current_height < 50:
            c.showPage()
            current_height = height - 50

c.save()  # Save the PDF
