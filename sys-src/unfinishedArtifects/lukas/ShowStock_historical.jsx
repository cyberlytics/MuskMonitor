import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import './ShowStock.css';

function ShowStock() {
  const [data, setData] = useState([]);
  const [tweets, setTweets] = useState([]);
  const [selectedDataKey, setSelectedDataKey] = useState('Schluss');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [showSecondGraph, setShowSecondGraph] = useState(false);

  useEffect(() => {
    fetch('/historical_data.json')
      .then(response => response.json())
      .then(data => {
        const formattedData = data.map(item => ({
          Datum: item.Datum,
          Schluss: parseFloat(item["Schluss/Letzter"].replace('$', '')),
          Volumen: item.Volumen,
          Eröffnungskurs: parseFloat(item["Eröffnungskurs"].replace('$', '')),
          Hoch: parseFloat(item.Hoch.replace('$', '')),
          Tief: parseFloat(item.Tief.replace('$', ''))
        }));
        setData(formattedData.reverse());
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
          Schluss: null,
          Volumen: null,
          Eröffnungskurs: null,
          Hoch: null,
          Tief: null
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
      <div className="form-container">
        <div className="select-container">
          <label htmlFor="dataKey">Kursdaten: </label>
          <select id="dataKey" value={selectedDataKey} onChange={handleChange}>
            <option value="Schluss">Schluss</option>
            <option value="Eröffnungskurs">Eröffnungskurs</option>
            <option value="Hoch">Hoch</option>
            <option value="Tief">Tief</option>
          </select>
        </div>
        <div className="input-container">
          <label htmlFor="startDate">Anfangsdatum: </label>
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