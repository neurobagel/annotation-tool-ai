# flake8: noqa: E501
import argparse
import json
from typing import Union
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import os
from fastapi.middleware.cors import CORSMiddleware


from processing import process_file




app = FastAPI(
    title="Data Annotation, But Make It Effortless with LLM Magic",
    description="""
    This API processes a TSV file and returns a JSON file with LLM-derived annotations annotations. \n\n
    Instructions:\n
    1. Upload a TSV file using the /process/ endpoint.\n
        Expand the /process/ section and click on "Try it out".\n
        Choose your preferred coding system currently "cogatlas" and "snomed" are supported.\n
        Choose your preferred response type currently "file" and "json" are supported.\n
        Click on "Choose File" and select a TSV file to upload.\n

    2. Hit the Execute button and the API will process the file and return a JSON (file) with the annotations.\n
        (Please be patient, the magic takes a while to happen...like really a while)\n""",
)



app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "*"
    ],  # --> Change this to the domain of the frontend in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process/", response_model=None)  # type: ignore
async def process_files(
    file: UploadFile = File(...),
    code_system: str = Query("cogatlas", enum=["cogatlas", "snomed"]),
    response_type: str = Query("file", enum=["file", "json"]),
) -> Union[FileResponse, JSONResponse, None]:
    file_location: str = f"temp_{file.filename}"

    # Save the uploaded file to a temporary location
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    json_file: str = f"{file_location}.json"

    # Process the file and generate the JSON
    process_file(file_location, json_file, code_system)

    if response_type == "file":
        # Return the JSON file as a downloadable response
        if os.path.exists(json_file):
            return FileResponse(
                path=json_file,
                filename=os.path.basename(json_file),
                media_type="application/json",
            )
        else:
            raise HTTPException(
                status_code=500, detail="File processing failed"
            )

    elif response_type == "json":
        # Return JSON response directly
        if os.path.exists(json_file):
            with open(json_file, "r") as f:
                json_content = json.load(f)
            return JSONResponse(content=json_content)
        else:
            return JSONResponse(
                content={"error": "File processing failed"}, status_code=500
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid response type")


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


        "--port", type=int, default=9000, help="Port to run the server on"

    )

    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)
