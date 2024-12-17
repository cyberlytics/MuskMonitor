import React from "react";
import TimeSeriesDisplay from "../components/timeSeriesDisplay";
import HamburgerMenu from "../components/HamburgerMenu.jsx";

export default function ShowTweets() {
  return (
    <div className="stock-page">
      <HamburgerMenu />
      <div className="content">
        <TimeSeriesDisplay filePath="/tweets.json" interval={2000} />
      </div>
    </div>
  );
}
