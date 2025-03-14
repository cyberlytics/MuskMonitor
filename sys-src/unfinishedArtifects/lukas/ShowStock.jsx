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

  useEffect(() => {
    const API_KEY = 'BJ22JP64AWPTKJN2';
    const symbol = 'TSLA';
    
    axios.get(`https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${symbol}&outputsize=full&apikey=${API_KEY}`)
      .then(response => {
        const timeSeries = response.data['Time Series (Daily)'];
        const formattedData = Object.keys(timeSeries).map(date => ({
          Datum: date,
          open: parseFloat(timeSeries[date]['1. open']),
          high: parseFloat(timeSeries[date]['2. high']),
          low: parseFloat(timeSeries[date]['3. low']),
          close: parseFloat(timeSeries[date]['4. close']),
          volume: parseInt(timeSeries[date]['5. volume'])
        }));
        setData(formattedData.reverse());

        // Daten in tsla.json speichern
        const blob = new Blob([JSON.stringify(formattedData, null, 4)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'tsla.json';
        a.click();
        URL.revokeObjectURL(url);
      });

    fetch('/tweets.json')
      .then(response => response.json())
      .then(data => {
        setTweets(data);
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

  const filteredData = data.filter(item => {
    const itemDate = new Date(item.Datum);
    const start = startDate ? new Date(startDate) : new Date('1900-01-01');
    const end = endDate ? new Date(endDate) : new Date();
    return itemDate >= start && itemDate <= end;
  });

  const secondGraphData = filteredData.map(item => ({
    ...item,
    [selectedDataKey]: item[selectedDataKey] - 5
  }));

  const extendedData = [...filteredData];
  if (endDate) {
    const lastDate = new Date(filteredData[filteredData.length - 1]?.Datum);
    const end = new Date(endDate);
    if (lastDate < end) {
      while (lastDate < end) {
        lastDate.setDate(lastDate.getDate() + 1);
        extendedData.push({
          Datum: lastDate.toISOString().split('T')[0],
          open: null,
          high: null,
          low: null,
          close: null,
          volume: null
        });
      }
    }
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const tweet = tweets.find(tweet => tweet.Datum === label);
      return (
        <div className="custom-tooltip">
          <p className="label">{`Datum: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={`item-${index}`} style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value}`}
            </p>
          ))}
          {tweet && <p className="tweet">{`Tweet: ${tweet.Tweet}`}</p>}
        </div>
      );
    }

    return null;
  };

  const CustomDot = (props) => {
    const { cx, cy, value, payload } = props;
    const tweet = tweets.find(tweet => tweet.Datum === payload.Datum);
    if (tweet) {
      return (
        <circle cx={cx} cy={cy} r={5} fill="red" stroke="none" />
      );
    }
    return null;
  };

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
      <div className="input-container">
        <label htmlFor="startDate">Start Date: </label>
        <input type="date" id="startDate" value={startDate} onChange={handleStartDateChange} />
      </div>
      <div className="input-container">
        <label htmlFor="endDate">End Date: </label>
        <input type="date" id="endDate" value={endDate} onChange={handleEndDateChange} />
      </div>
      <div className="input-container">
        <label htmlFor="showSecondGraph">Vorhersage: </label>
        <input type="checkbox" id="showSecondGraph" checked={showSecondGraph} onChange={handleCheckboxChange} />
      </div>
      {extendedData.length > 0 ? (
        <LineChart width={1200} height={600} data={extendedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="Datum" />
          <YAxis />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line type="monotone" dataKey={selectedDataKey} stroke="#8884d8" name="Original" dot={<CustomDot />} />
          {showSecondGraph && (
            <Line type="monotone" dataKey={selectedDataKey} data={extendedData.map(item => ({
              ...item,
              [selectedDataKey]: item[selectedDataKey] ? item[selectedDataKey] - 5 : null
            }))} stroke="#82ca9d" name="Vorhersage" dot={<CustomDot />} />
          )}
        </LineChart>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}

export default ShowStock;