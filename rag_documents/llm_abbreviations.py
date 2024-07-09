import argparse
import json
from typing import List
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import re
import os


def get_diagnosis_labels(input_file: str) -> List[str]:
    with open(input_file, "r") as file:
        original_terms = json.load(file)
    labels = [
        term.get("label", term.get("Label", "")).strip()
        for term in original_terms
    ]
    return labels


def generate_abbreviations_pdf(abbreviations_input_filename: str) -> None:
    with open(abbreviations_input_filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    input_filename = abbreviations_input_filename.split(".")[0]
    output_filename = f"{input_filename}.pdf"
    c = canvas.Canvas(output_filename, pagesize=letter)
    width, height = letter
    line_height = 14
    current_height = height - 50

    for entry in data:
        label = entry["label"]
        for abbreviation in entry["abbreviations"]:
            line = f"{abbreviation}: {label}"
            c.drawString(50, current_height, line)
            current_height -= line_height
            if current_height < 50:
                c.showPage()
                current_height = height - 50

    c.save()


def main(input_file: str) -> None:
    labels = get_diagnosis_labels(input_file)
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
    chain = prompt | llm

    # Extract directory and filename from input_file
    directory = os.path.dirname(input_file)
    filename = os.path.basename(input_file)

    for term in labels:
        print(term)
        response = chain.invoke({"term": term})
        print(response)
        response = str(response)
        match = re.search(r"content='(.*?)'", response)
        if match:
            content_part = match.group(1)
        else:
            print("No content part found in response.")
            content_part = ""
        abbreviations_list = (
            [abbr.strip() for abbr in content_part.split(",")]
            if content_part
            else []
        )
        result_dict = {"label": term, "abbreviations": abbreviations_list}
        if not abbreviations_list:
            print("No abbreviations found for term:", term)
            continue

        # Add "abbreviations_" prefix to the filename
        new_filename = f"abbreviations_{filename}"

        # Construct the new path with the modified filename
        abbreviations_input_filename = os.path.join(directory, new_filename)
        print(abbreviations_input_filename)

        try:
            with open(abbreviations_input_filename, "r") as file:
                data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
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

        with open(abbreviations_input_filename, "w") as file:
            json.dump(data, file, indent=4)
            file.write("\n")
        print(result_dict)

    # Correctly construct the path for the PDF generation
    abbreviations_input_filename_for_pdf = os.path.join(
        directory, f"abbreviations_{os.path.basename(input_file)}"
    )
    generate_abbreviations_pdf(abbreviations_input_filename_for_pdf)


if __name__ == "__main__":
    # Parse command line arguments for input file
    parser = argparse.ArgumentParser(description="Process terms.")
    parser.add_argument(
        "--input", type=str, help="The JSON file containing diagnosis terms."
    )
    args = parser.parse_args()
    main(args.input)
