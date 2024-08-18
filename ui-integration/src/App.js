import React, { useState, useEffect } from "react";
import axios from "axios";
import "bootstrap/dist/css/bootstrap.min.css";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [codeSystem, setCodeSystem] = useState("cogatlas");
  const [responseType, setResponseType] = useState("file");
  const [responseData, setResponseData] = useState(null);
  const [diagnosisOptions, setDiagnosisOptions] = useState({});
  const [selectedDiagnosis, setSelectedDiagnosis] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleDiagnosisChange = (columnName, levelKey, selectedValue) => {
    setSelectedDiagnosis((prevState) => ({
      ...prevState,
      [columnName]: {
        ...prevState[columnName],
        [levelKey]: selectedValue,
      },
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("code_system", codeSystem);
    formData.append("response_type", responseType);

    try {
      const response = await axios.post(
        "http://127.0.0.1:3003/process/",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          responseType: responseType === "json" ? "json" : "blob",
        }
      );

      if (responseType === "json") {
        setResponseData(response.data);
        extractDiagnosisOptions(response.data);
      } else if (responseType === "file") {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const a = document.createElement("a");
        a.href = url;
        a.download = `${file.name}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (error) {
      console.error("Error:", error);
      setError(`Failed to process the request: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const extractDiagnosisOptions = (data) => {
    const diagnosisColumns = {};
    Object.keys(data).forEach((columnName) => {
      const annotations = data[columnName]?.Annotations;
      if (annotations?.IsAbout?.TermURL?.includes("Diagnosis")) {
        const levels = annotations.Levels || {};
        diagnosisColumns[columnName] = {};

        Object.keys(levels).forEach((levelKey) => {
          const nestedLevels = levels[levelKey] || {};
          const options = Object.keys(nestedLevels).map((key) => ({
            label: nestedLevels[key]?.Label || key,
            value: key,
            termUrl: nestedLevels[key]?.TermURL,
          }));
          diagnosisColumns[columnName][levelKey] = options;
        });
      }
    });
    setDiagnosisOptions(diagnosisColumns);
  };

  useEffect(() => {
    if (responseData) {
      console.log("responseData updated:", responseData);
    }
  }, [responseData]);

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-lg-6 col-md-8">
          <div className="card shadow-sm">
            <div className="card-body">
              <h1 className="card-title text-center mb-4">
                Data Annotation, but make it Effortless with LLM Magic
              </h1>

              <div className="mb-4">
                <h4 className="text">Instructions</h4>
                <p className="text">
                  1. Upload your TSV file by selecting it using the "Choose File" button.
                  <br /><br />
                  2. Choose the coding system you prefer for assessment tools: "Cognitive Atlas" or "SNOMED".
                  <br /><br />
                  3. Select the response type: "File" for downloading a JSON file or "JSON" to view the response directly.
                  <br /><br />
                  4. Click "Submit" to process the file.
                  <br /><br />
                  <b>Please be patient...the magic takes a while to happen....like really a while</b>
                  <br /><br />
                  5. If you chose "File" as the response type, a JSON file will be automatically downloaded. If "JSON" was selected, the result will be displayed below.
                </p>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="fileInput" className="form-label">Upload File</label>
                  <input type="file" className="form-control" id="fileInput" onChange={handleFileChange} required />
                </div>
                <div className="mb-3">
                  <label htmlFor="codeSystemSelect" className="form-label">Code System</label>
                  <select id="codeSystemSelect" className="form-select" value={codeSystem} onChange={(e) => setCodeSystem(e.target.value)} required>
                    <option value="cogatlas">Cognitive Atlas</option>
                    <option value="snomed">SNOMED</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label htmlFor="responseTypeSelect" className="form-label">Response Type</label>
                  <select id="responseTypeSelect" className="form-select" value={responseType} onChange={(e) => setResponseType(e.target.value)} required>
                    <option value="file">File</option>
                    <option value="json">JSON</option>
                  </select>
                </div>
                <div className="d-grid">
                  <button type="submit" className="btn btn-primary btn-block">Submit</button>
                </div>
              </form>

              {loading && (
                <div className="text-center mt-3">
                  <div className="spinner-border" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </div>
                </div>
              )}

              {error && (
                <div className="text-center text-danger mt-3">{error}</div>
              )}

              {responseType === "json" && responseData && !loading && (
                <>
                  {Object.keys(diagnosisOptions).length > 0 && (
                    <div className="mt-4">
                      <h4 className="h5">Select Diagnosis Options</h4>
                      {Object.keys(diagnosisOptions).map((columnName) => (
                        <div key={columnName} className="mb-3">
                          <h5>{columnName} Diagnosis Levels</h5>
                          {Object.keys(diagnosisOptions[columnName]).map((levelKey) => (
                            <div key={levelKey} className="mb-3">
                              <label htmlFor={`${columnName}-${levelKey}Select`} className="form-label">
                                {levelKey} Level
                              </label>
                              <select
                                id={`${columnName}-${levelKey}Select`}
                                className="form-select"
                                value={selectedDiagnosis[columnName]?.[levelKey] || ""}
                                onChange={(e) =>
                                  handleDiagnosisChange(columnName, levelKey, e.target.value)
                                }
                              >
                                <option value="">Select a level</option>
                                {diagnosisOptions[columnName][levelKey].map((option) => (
                                  <option key={option.value} value={option.value}>
                                    {option.label} - {option.termUrl}
                                  </option>
                                ))}
                              </select>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mt-4">
                    <h2 className="h5">JSON Response:</h2>
                    <pre className="bg-light p-3 rounded">
                      {JSON.stringify(responseData, null, 2)}
                    </pre>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FileUpload;
