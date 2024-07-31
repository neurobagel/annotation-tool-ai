from typing import Dict
from categorization.llm_categorization import llm_invocation
from parsing.json_parsing import (
    convert_tsv_to_dict,
    process_parsed_output,
    update_json_file,
    tsv_to_json,
)


def process_file(
    file_path: str, json_file: str, code_system: str
) -> Dict[str, str]:
    columns_dict = convert_tsv_to_dict(file_path)
    tsv_to_json(file_path, json_file)

    results = {}

    for key, value in columns_dict.items():
        try:
            input_dict = {key: value}
            llm_response = llm_invocation(input_dict, code_system)
            result = process_parsed_output(llm_response, code_system)  # type: ignore # noqa: E501
            results[key] = result
            update_json_file(result, json_file, key)
        except Exception as e:
            results[key] = {"error": str(e)}

    return results
