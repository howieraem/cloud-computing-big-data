import React, { useState } from "react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const SearchForm = ({ handleSubmit, history }) => {
  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable
  } = useSpeechRecognition();

  const [searchEntry, setSearchEntry] = useState("");
  const updateSearchInput = e => {
    resetTranscript();
    setSearchEntry(e.target.value);
  };

  const inputVal = listening ? "" : (searchEntry || transcript);
  const isEmpty = !Boolean(inputVal.trim());

  return (
    <form
      className="search-form"
      onSubmit={e => handleSubmit(e, history, inputVal)}
    >
      <input
        type="search"
        name="search"
        placeholder="Search..."
        onChange={updateSearchInput}
        value={inputVal}
      />
      { browserSupportsSpeechRecognition && isMicrophoneAvailable && (
        <>
          <button 
            onClick={e => { e.preventDefault(); resetTranscript(); setSearchEntry(""); SpeechRecognition.startListening(); }} 
            className={`search-button active`}
            disabled={listening}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              width="24" 
              height="24" 
              viewBox="0 0 24 24"
            >
              <path 
                d="M12 2c1.103 0 2 .897 2 2v7c0 1.103-.897 2-2 2s-2-.897-2-2v-7c0-1.103.897-2 2-2zm0-2c-2.209 0-4 1.791-4 4v7c0 2.209 1.791 4 4 4s4-1.791 4-4v-7c0-2.209-1.791-4-4-4zm8 9v2c0 4.418-3.582 8-8 8s-8-3.582-8-8v-2h2v2c0 3.309 2.691 6 6 6s6-2.691 6-6v-2h2zm-7 13v-2h-2v2h-4v2h10v-2h-4z"
                fill="#ffffff"
                fillRule="evenodd"
              />
            </svg>
          </button>
        </>
      )}
      <button
        type="submit"
        className={`search-button active`}
        disabled={isEmpty}
      >
        <svg height="32" width="32">
          <path
            d="M19.427 21.427a8.5 8.5 0 1 1 2-2l5.585 5.585c.55.55.546 1.43 0 1.976l-.024.024a1.399 1.399 0 0 1-1.976 0l-5.585-5.585zM14.5 21a6.5 6.5 0 1 0 0-13 6.5 6.5 0 0 0 0 13z"
            fill="#ffffff"
            fillRule="evenodd"
          />
        </svg>
      </button>
    </form>
  );
};

export default SearchForm;
