import axios from 'axios';
import React, { useRef, useState } from "react";
import { useHistory } from 'react-router-dom';
import { WithContext as ReactTags } from 'react-tag-input';
import { v4 as uuidv4 } from 'uuid';
import { API_UPLOAD, API_KEY } from '../api/config';

const KeyCodes = {
  comma: 188,
  enter: 13,
};

const delimiters = [KeyCodes.comma, KeyCodes.enter];

const UploadForm = () => {
  let hist = useHistory();

  const fileBrowseForm = document.getElementById('fileBrowse');
  const inputFile = useRef(null) 
  const [fileMeta, setFileMeta] = useState(null);
  const [fileUrl, setFileUrl] = useState("");

  const [labels, setLabels] = useState([]);

  const resetFile = () => {
    setFileMeta(null);
    setFileUrl("");
    fileBrowseForm.value = '';
    setLabels([]);
  }

  const updateInput = e => {
    const metaData = e.target.files[0];
    if (metaData) {
      if (metaData.type === 'image/jpeg' || metaData.type === 'image/png') {
        setFileMeta(metaData);
        setFileUrl(URL.createObjectURL(metaData));
      } else {
        resetFile();
        alert("File not supported: You can only upload JPEG or PNG images!");
      }
    } else {
      resetFile();
    }
  };

  const handleDelLabel = i => {
    setLabels(labels.filter((label, idx) => idx !== i));
  }

  const handleAddLabel = label => {
    setLabels([...labels, label]);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (fileMeta) {
      try {
        const response = await axios({
          method: "put",
          url: `${API_UPLOAD}/${uuidv4()}.${fileMeta.name.split('.').pop()}`,
          data: fileMeta,
          headers: { 
            "x-api-key": API_KEY,
            "Content-Type": fileMeta.type, 
            "x-amz-meta-customLabels": JSON.stringify(labels.map(label => label.text.replace(/(\r\n|\n|\r)/gm, "")))
          }
        });
        if (response.status === 200) {
          alert("The photo was uploaded successfully!");
          hist.push('/');
        } else {
          alert(`Upload status code ${response.status}`);
        }
      } catch (err) {
        if (err.response) {
          alert(`An error occurred: ${err.response.data}`);
        } else {
          alert(`An error occurred: ${err.message}`);
        }
      }
    }
  }

  const isEmpty = !Boolean(fileUrl);
  // console.log(inputFile, fileMeta);

  return (
    <>
      <h2>Upload a Photo</h2>
      <form
        className="search-form"
        onSubmit={handleSubmit}
      >
        <input
          type='file' 
          name='file'
          id='fileBrowse'
          placeholder="Browse..."
          ref={inputFile}
          onChange={updateInput}
          accept=".png, .jpg, .jpeg"
        />
        { fileBrowseForm && fileBrowseForm.value && (
          <button
            type="submit"
            className={`search-button active`}
            onClick={e => { e.preventDefault(); resetFile(); }} 
          >
            Clear
          </button>
        )}
        <button
          type="submit"
          className={`search-button active`}
          disabled={isEmpty}
        >
          Upload
        </button>
      </form>
      <div className="label-form">
        <ReactTags 
          inline={false}
          tags={labels}
          handleDelete={handleDelLabel}
          handleAddition={handleAddLabel}
          delimiters={delimiters}
          placeholder="Add a new label"
        />
      </div>
      {fileUrl && (
        <div className="preview">
          <img src={fileUrl} alt={`${fileMeta ? fileMeta.name : ''}_preview`} style={{ maxWidth: '100%', maxHeight: '100%' }} />
        </div>
      )}
    </>
  );
};

export default UploadForm;
