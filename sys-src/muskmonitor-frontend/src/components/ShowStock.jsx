import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function ShowStock() {
  const [data, setData] = useState([]);
  const [selectedDataKey, setSelectedDataKey] = useState('Schluss');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

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
        setData(formattedData.reverse()); // Daten umkehren
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

  const filteredData = data.filter(item => {
    const itemDate = new Date(item.Datum);
    const start = startDate ? new Date(startDate) : new Date('1900-01-01');
    const end = endDate ? new Date(endDate) : new Date();
    return itemDate >= start && itemDate <= end;
  });

  return (
    <div>
      <h1>Stock Data Visualization</h1>
      <label htmlFor="dataKey">Select Data Key: </label>
      <select id="dataKey" value={selectedDataKey} onChange={handleChange}>
        <option value="Schluss">Schluss</option>
        <option value="Eröffnungskurs">Eröffnungskurs</option>
        <option value="Hoch">Hoch</option>
        <option value="Tief">Tief</option>
      </select>
      <br />
      <label htmlFor="startDate">Start Date: </label>
      <input type="date" id="startDate" value={startDate} onChange={handleStartDateChange} />
      <label htmlFor="endDate">End Date: </label>
      <input type="date" id="endDate" value={endDate} onChange={handleEndDateChange} />
      {filteredData.length > 0 ? (
        <LineChart width={1200} height={600} data={filteredData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="Datum" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey={selectedDataKey} stroke="#8884d8" />
        </LineChart>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}

export default ShowStock;