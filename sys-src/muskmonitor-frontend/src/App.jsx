import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import ShowTweets from "./pages/show_tweets";
import Home from "./pages/home";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/tweets" element={<ShowTweets />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
