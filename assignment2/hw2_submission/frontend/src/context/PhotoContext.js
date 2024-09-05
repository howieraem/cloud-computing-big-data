import React, { createContext, useState } from "react";
import axios from "axios";
import { API_SEARCH, API_KEY } from "../api/config";
export const PhotoContext = createContext();

const PhotoContextProvider = props => {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const runSearch = query => {
    setLoading(true);
    axios
      .get(
        API_SEARCH + `?q=${query}`,
        { headers: { "x-api-key": API_KEY } }
      )
      .then(response => {
        setImages(response.data);
        setLoading(false);
        // console.log(response.data);
      })
      .catch(error => {
        console.log(
          "Encountered an error with fetching and parsing data",
          error
        );
      });
  };
  return (
    <PhotoContext.Provider value={{ images, loading, runSearch }}>
      {props.children}
    </PhotoContext.Provider>
  );
};

export default PhotoContextProvider;
