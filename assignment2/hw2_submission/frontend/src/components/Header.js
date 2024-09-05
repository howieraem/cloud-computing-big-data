import React from "react";
import { useHistory } from "react-router-dom";
import SearchForm from "./SearchForm";

const Header = ({ history, handleSubmit, renderForm, renderBtn }) => {
  let hist = useHistory();

  return (
    <div>
      <h1><a href="/">Voice Album</a></h1>
      {renderBtn && (
        <button 
          onClick={e => { e.preventDefault(); hist.push('/upload'); }} 
          className={`page-button`}
        >
          Upload a Photo
        </button>
      )}
      {renderForm && <SearchForm history={history} handleSubmit={handleSubmit} />}
    </div>
  );
};

export default Header;
