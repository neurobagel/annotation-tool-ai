import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';


function FileUpload() {
  const [file, setFile] = useState(null);
  const [codeSystem, setCodeSystem] = useState('cogatlas');
  const [responseType, setResponseType] = useState('file');
  const [responseData, setResponseData] = useState(null);
  const [loading, setLoading] = useState(false); // Add loading state

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true); // Set loading to true when request starts

    const formData = new FormData();
    formData.append('file', file);
    formData.append('code_system', codeSystem);
    formData.append('response_type', responseType);

    try {
      const response = await fetch('http://127.0.0.1:8000/process/', {
        method: 'POST',
        body: formData,
      });

      if (responseType === 'json') {
        const data = await response.json();
        setResponseData(data);
      } else if (responseType === 'file') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${file.name}.json`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false); // Set loading to false when request completes or fails
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-lg-6 col-md-8">
          <div className="card shadow-sm">
            <div className="card-body">
              <h1 className="card-title text-center mb-4">Data Annotation, but make it Effortless with LLM Magic</h1>
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="fileInput" className="form-label">Upload File</label>
                  <input 
                    type="file" 
                    className="form-control" 
                    id="fileInput" 
                    onChange={handleFileChange} 
                  />
                </div>
                <div className="mb-3">
                  <label htmlFor="codeSystemSelect" className="form-label">Code System</label>
                  <select
                    id="codeSystemSelect"
                    className="form-select"
                    value={codeSystem}
                    onChange={(e) => setCodeSystem(e.target.value)}
                  >
                    <option value="cogatlas">Cognitive Atlas</option>
                    <option value="snomed">SNOMED</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label htmlFor="responseTypeSelect" className="form-label">Response Type</label>
                  <select
                    id="responseTypeSelect"
                    className="form-select"
                    value={responseType}
                    onChange={(e) => setResponseType(e.target.value)}
                  >
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

              {responseType === 'json' && responseData && !loading && (
                <div className="mt-4">
                  <h2 className="h5">JSON Response:</h2>
                  <pre className="bg-light p-3 rounded">{JSON.stringify(responseData, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FileUpload;