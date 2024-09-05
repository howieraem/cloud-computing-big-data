import React from "react";
import PhotoContextProvider from "./context/PhotoContext";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import Header from "./components/Header";
import Search from "./components/Search";
import NotFound from "./components/NotFound";
import UploadForm from "./components/UploadForm";

const App = () => {
  const [renderSearchForm, setRenderSearchForm] = React.useState(true);
  const [renderUploadBtn, setRenderUploadBtn] = React.useState(true);

  // Prevent page reload, clear input, set URL and push history on submit
  const handleSubmit = (e, history, searchInput) => {
    e.preventDefault();
    e.currentTarget.reset();
    let url = `/search/${searchInput}`;
    history.push(url);
  };

  return (
    <PhotoContextProvider>
      <BrowserRouter>
        <div className="container">
          <Route
            render={props => (
              <Header
                handleSubmit={handleSubmit}
                history={props.history}
                renderForm={renderSearchForm}
                renderBtn={renderUploadBtn}
              />
            )}
          />
          <Switch>
            <Route exact path="/" render={() => { setRenderSearchForm(true); setRenderUploadBtn(true); }} />
            <Route
              path="/search/:searchInput"
              render={props => {
                setRenderSearchForm(true);
                setRenderUploadBtn(true);
                return <Search searchTerm={props.match.params.searchInput} />
              }}
            />
            <Route 
              exact path="/upload" 
              render={() => {
                setRenderSearchForm(false);
                setRenderUploadBtn(false);
                return <UploadForm />
              }} 
            />
            <Route component={NotFound} />
          </Switch>
        </div>
      </BrowserRouter>
    </PhotoContextProvider>
  );
}

export default App;
