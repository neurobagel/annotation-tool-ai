import json
from typing import Any, Dict, Union

from app.factories.annotation_factories.factory_creator import FactoryCreator


def process_llm_output(
    parsed_output: Union[Dict[str, Union[str, Dict[str, str], None]], None]
) -> Union[str, Any]:
    if parsed_output is None:
        return json.dumps(
            {
                "error": "The provided content does not fit the current Neurobagel data model entities. Be patient...we are working on it."  # noqa: E501
            }
        )

    term_url = parsed_output.get("TermURL")

    if not isinstance(term_url, str):
        return "No valid TermURL found in the parsed output"

    factory = FactoryCreator.get_factory(term_url)

    if factory is None:
        return f"Error: No factory found for TermURL: {term_url}"

    return factory.create_annotation(parsed_output)
