import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function ShowStock() {
  const [data, setData] = useState([]);
  const [tweets, setTweets] = useState([]);
  const [selectedDataKey, setSelectedDataKey] = useState('close');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showSecondGraph, setShowSecondGraph] = useState(false);
  const [predictions, setPredictions] = useState(null);

  useEffect(() => {
    // Fetch stock data
    fetch("/get_stock_data", {   
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
    })
    .then(response => response.json())
    .then(stock_data => {
      setData(stock_data);
    })
    .catch(err => {
      console.error("Error fetching stock data:", err);
    });
  
    // Fetch tweets
    fetch("/get_important_tweets")
      .then(response => response.json())
      .then(tweet_data => {
        setTweets(tweet_data);
      })
      .catch(err => {
        console.error("Error fetching tweets:", err);
      });
  
    // Fetch prediction results
    fetch("/get_prediction_results")
      .then(response => response.json())
      .then(pred_data => {
        setPredictions(pred_data);
      })
      .catch(() => {
        console.log("No predictions available yet.");
      });
  }, []);
  

  const handleChange = (event) => {
    setSelectedDataKey(event.target.value);
  };

  const handleStartDateChange = (event) => {
    setStartDate(event.target.value);
  };

  const handleEndDateChange = (event) => {
    setEndDate(event.target.value);
  };

  const handleCheckboxChange = (event) => {
    setShowSecondGraph(event.target.checked);
  };

  // Filter stock data based on date range
  const filteredData = data.filter(item => {
    const itemDate = new Date(item.Datum);
    const start = startDate ? new Date(startDate) : new Date('1900-01-01');
    const end = endDate ? new Date(endDate) : new Date();
    return itemDate >= start && itemDate <= end;
  });

  // Combine predictions and original stock data based on the date
  const combinedData = () => {
    // Clone the filtered original data
    let combined = [...filteredData];
    
    // Create a map for quick lookup of data by date
    const combinedMap = new Map();
    combined.forEach(item => {
      const formattedDate = new Date(item.Datum).toISOString().split('T')[0]; // Format the date to 'YYYY-MM-DD'
      combinedMap.set(formattedDate, { ...item });
    });
  
    // Merge predicted values into the combined data
    if (predictions?.predicted_values) {
      predictions.predicted_values.forEach(({ date, value }) => {
        const formattedDate = new Date(date).toISOString().split('T')[0]; // Format the date to 'YYYY-MM-DD'
        
        // Only add predicted data if it falls within the selected date range
        if (isDateInRange(formattedDate, false)) {  // Future predictions are allowed beyond the end date
          if (combinedMap.has(formattedDate)) {
            // Update existing entry with predicted value
            combinedMap.get(formattedDate).predicted = value;
          } else {
            // If no entry for that date, create a new one for prediction
            combinedMap.set(formattedDate, {
              Datum: formattedDate,
              predicted: value,
            });
          }
        }
      });
    }
  
    // Merge future predictions into the combined data
    if (predictions?.future_predictions) {
      predictions.future_predictions.forEach(({ date, value }) => {
        const formattedDate = new Date(date).toISOString().split('T')[0]; // Format the date to 'YYYY-MM-DD'
        
        // Always include future predictions regardless of the end date
        if (isDateInRange(formattedDate, true)) {  // Future predictions are always included
          if (combinedMap.has(formattedDate)) {
            // Update existing entry with future value
            combinedMap.get(formattedDate).future = value;
          } else {
            // If no entry for that date, create a new one for future prediction
            combinedMap.set(formattedDate, {
              Datum: formattedDate,
              future: value,
            });
          }
        }
      });
    }
  
    // Convert the map back to an array and sort by Datum
    combined = Array.from(combinedMap.values()).sort((a, b) => new Date(a.Datum) - new Date(b.Datum));
  
    return combined;
  };
  
  // Helper function to check if the date is within the range
  const isDateInRange = (date, isFuturePrediction = false) => {
    const start = startDate ? new Date(startDate) : new Date('1900-01-01');
    const end = endDate ? new Date(endDate) : new Date();
  
    // If it's a future prediction, we ignore the `endDate` check
    if (isFuturePrediction) {
      return new Date(date) >= start;
    }
  
    // For regular stock data and predictions, respect both startDate and endDate
    return new Date(date) >= start && new Date(date) <= end;
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const tweet = tweets.find(tweet => tweet.Date.includes(label));
      return (
        <div className="custom-tooltip">
          <p className="label">{`Datum: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={`item-${index}`} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value}`}
            </p>
          ))}
          {tweet && <p className="tweet">{`Tweet: ${tweet.Text}`}</p>}
        </div>
      );
    }

    return null;
  };

  const CustomDot = (props) => {
    const { cx, cy, value, payload } = props;
    const tweet = tweets.find(tweet => tweet.Date.includes(payload.Datum));
    if (tweet) {
      return (
        <circle cx={cx} cy={cy} r={5} fill="red" stroke="none" />
      );
    }
    return null;
  };

  const combinedChartData = combinedData(); // Get the merged data

  return (
    <div>
      <h1>Stock Data Visualization</h1>
      <label htmlFor="dataKey">Select Data Key: </label>
      <select id="dataKey" value={selectedDataKey} onChange={handleChange}>
        <option value="open">Open</option>
        <option value="high">High</option>
        <option value="low">Low</option>
        <option value="close">Close</option>
        <option value="volume">Volume</option>
      </select>
      <br />
      <label htmlFor="startDate">Start Date: </label>
      <input type="date" id="startDate" value={startDate} onChange={handleStartDateChange} />
      <label htmlFor="endDate">End Date: </label>
      <input type="date" id="endDate" value={endDate} onChange={handleEndDateChange} />
      <br />
      <label htmlFor="showSecondGraph">Show Predictions: </label>
      <input type="checkbox" id="showSecondGraph" checked={showSecondGraph} onChange={handleCheckboxChange} />
      {combinedChartData.length > 0 ? (
        <LineChart width={1200} height={600} data={combinedChartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="Datum" />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line type="monotone" dataKey={selectedDataKey} stroke="#8884d8" name="Original" dot={<CustomDot />} />
          {showSecondGraph && predictions && (
            <>
              <Line
                type="monotone"
                dataKey="predicted"
                stroke="#82ca9d"
                name="Predicted"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="future"
                stroke="#FF5733"
                name="Future Predictions"
              />
            </>
          )}
        </LineChart>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}

export default ShowStock;
