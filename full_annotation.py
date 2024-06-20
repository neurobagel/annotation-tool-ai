from categorization.bin.llm_categorization import llm_invocation
from parsing.bin.json_parsing import (
    convert_tsv_to_dict,
    process_parsed_output,
    update_json_file,
    tsv_to_json,
)


if __name__ == "__main__":

    file_path = "participants.tsv"
    json_file = "output.json"

    columns_dict = convert_tsv_to_dict(file_path)

    tsv_to_json(file_path, json_file)

    # Create output for each column
    for key, value in columns_dict.items():
        print("Processing column:", key)
        try:
            # Invoke the chain with the input data
            input_dict = {key: value}
            print(key)
            # Column information is inserted in prompt template
            llm_response = llm_invocation(input_dict)

        except Exception as e:
            print("Error processing column:", key)
            print("Error message:", e)

        result = process_parsed_output(llm_response)
        print(result)
        update_json_file(result, "output.json", key)
