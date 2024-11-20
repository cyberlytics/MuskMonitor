import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function ShowStock() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('sys-src\muskmonitor-frontend\public\historical_data.json')
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
        setData(formattedData);
      });
  }, []);

  return (
    <div>
      <h1>Stock Data Visualization</h1>
      <LineChart width={600} height={300} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="Datum" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="Schluss" stroke="#8884d8" />
        <Line type="monotone" dataKey="Eröffnungskurs" stroke="#82ca9d" />
        <Line type="monotone" dataKey="Hoch" stroke="#ffc658" />
        <Line type="monotone" dataKey="Tief" stroke="#ff7300" />
      </LineChart>
    </div>
  );
}

export default ShowStock;