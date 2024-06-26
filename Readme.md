# Annotation Tool AI


[Neurobagel's](https://www.neurobagel.org/) annotation tool-ai project aims at  taking BIDS-style [phenotypic data](https://github.com/neurobagel/annotation_tool/blob/main/cypress/fixtures/examples/good/ds003653_participant.tsv) and [corresponding data description files](https://github.com/neurobagel/annotation_tool/blob/main/cypress/fixtures/examples/good/ds003653_participant.json) and gives users a first pass annotation by employing LLMs which use the Neurobagel data model for preparation to inject that modeled data into Neurobagel's graph database for [federated querying](https://github.com/neurobagel/query-tool).

We are attempting to achieve this automation using LLMs (at present gemma) and various libraries like pydantic.


[Local Installation](#local-installation) |
[Details of the codebase ](#details-of-the-codebase) |
[License](#license)


## Local Installation

### Building and running



- clone the repo
`git clone https://github.com/neurobagel/annotation-tool-ai`

- create virtual environment
 `python3 -m venv venv`

 `source venv/bin/activate`

- set up pre-commit ( flake8, black, mypy)
 `pre-commit install`

- Install ollama (Currently the tool is supported only on linux ) 

`curl -fsSL https://ollama.com/install.sh | sh`


- complete installations 
 `pip install -r requirements.txt`



## Details of the codebase 

### Currently the development of the tool is divided into 2 aspects:

#### Parsing and obtaining the final structured output:
The codebase is designed to handle and annotate TSV data by converting it into JSON format. It leverages the Pydantic library to enforce data structures, ensuring the consistens and valid data throughout the annotation process.
The main components of the code include defining data structures for various annotation categories, handling the annotation of the categories itself and create a JSON file containing the annotations.

#### Categorization using LLMS and return the required structure of output for furhter processing:

The codebase is created to categorize/classify the columns present in the tsv input file into classes according to the already existing categories present in the neurobagel annotation tool. The LLM makes it predictions for a specific input string consisting of the column header and the column contents based on the examples provided to it beforehand in its promptemplate.
The various tasks carried out by this codebase mainly utilise Langchain,
the json library from python and the LLM 'Gemma' from Ollama.



## License

The Neurobagel Annotation-tool-AI  uses the [MIT License](https://github.com/neurobagel/annotation-tool-ai/blob/main/LICENSE).


