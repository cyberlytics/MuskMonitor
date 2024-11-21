import React from "react";
import TimeSeriesDisplay from "../components/timeSeriesDisplay";

export default function ShowTweets() {
  return (
    <div>
      <TimeSeriesDisplay filePath="/tweets.json" interval={2000} />
    </div>
  );
}
