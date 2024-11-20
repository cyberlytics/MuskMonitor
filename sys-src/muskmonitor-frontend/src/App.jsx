import React from 'react';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";
import ShowStock from './pages/show_stock.jsx';
import ShowTweets from './pages/show_tweets.jsx';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/show_stock" element={<ShowStock />} />
        <Route path="/show_tweets" element={<ShowTweets />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;