import argparse
from typing import Union
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import os

from processing import process_file

app = FastAPI()


@app.post("/process/")  # type: ignore
async def process_files(
    file: UploadFile = File(...), code_system: str = "cogatlas"
) -> Union[FileResponse, JSONResponse]:
    file_location: str = f"temp_{file.filename}"

    # Save the uploaded file to a temporary location
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    json_file: str = f"{file_location}.json"

    # Process the file and generate the JSON
    process_file(file_location, json_file, code_system)

    # Return the JSON file as a downloadable response
    if os.path.exists(json_file):
        return FileResponse(
            path=json_file,
            filename=os.path.basename(json_file),
            media_type="application/json",
        )
    else:
        return JSONResponse(
            content={"error": "File processing failed"}, status_code=500
        )


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(
        description="Run FastAPI server to process TSV file and return JSON output."  # noqa: E501
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the server on",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )

    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
