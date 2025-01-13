import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from pymongo import MongoClient


#  Datenbankabfrage
def fetch_data_from_db(start_date=None, end_date=None):
    try:
        # mongoClient = MongoClient("mongodb://root:root_password@stock-database:27017/")
        mongoClient = MongoClient("mongodb://stock-database:27017/")
        stockDB = mongoClient["stock_data"]
        telsaCollection = stockDB["tesla"]

        query = {}
        if start_date and end_date:
            query["Datum"] = {"$gte": start_date, "$lte": end_date}

        documents = list(telsaCollection.find(query).sort("Datum", 1))
        if not documents:
            print("Keine Daten gefunden für den angegebenen Zeitraum.")
            return pd.DataFrame()

        # Umwandlung der abgerufenen Daten in ein DataFrame
        df = pd.DataFrame(documents)
        df["Datum"] = pd.to_datetime(df["Datum"])
        df["Year"] = df["Datum"].dt.year
        df["Month"] = df["Datum"].dt.month

        return df[["Datum", "close", "open", "high", "low", "volume"]]
    except Exception as e:
        print(f"Fehler beim Abrufen der Daten aus der Datenbank: {e}")
        return pd.DataFrame()


# Datenvorbereitung
def prepare_data(df):
    dataset = df[["close", "open", "high", "low", "volume"]]
    data = dataset.values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset[["close"]].values)
    # Aufteilen in Trainings- und Testdaten
    train_size = int(len(data) * 0.75)
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size - 60 :]

    return train_data, test_data, scaler


# Daten für LSTM vorbereiten
def create_lstm_data(data, time_step=60):
    x_data = []
    y_data = []

    for i in range(time_step, len(data)):
        x_data.append(data[i - time_step : i, 0])  # Collect sequences
        y_data.append(data[i, 0])  # Collect the target value

    # Convert lists to numpy arrays first
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    # Convert numpy arrays to PyTorch tensors
    x_tensor = torch.tensor(x_data, dtype=torch.float32).unsqueeze(-1)  # Add a feature dimension
    y_tensor = torch.tensor(y_data, dtype=torch.float32).unsqueeze(-1)

    return x_tensor, y_tensor



# LSTM Modelldefinition
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm1 = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.lstm2 = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, output_size)

    def forward(self, x):
        out, _ = self.lstm1(x)
        out, _ = self.lstm2(out)
        out = out[:, -1, :]  # Nur den letzten Output verwenden
        out = torch.relu(self.fc1(out))
        out = torch.relu(self.fc2(out))
        out = self.fc3(out)
        return out


# Modelltraining
def train_lstm_model(
    x_train,
    y_train,
    input_size=1,
    hidden_size=50,
    output_size=1,
    epochs=100,
    batch_size=32,
):
    model = LSTMModel(input_size, hidden_size, output_size)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(epochs):
        model.train()
        for i in range(0, len(x_train), batch_size):
            x_batch = x_train[i : i + batch_size]
            y_batch = y_train[i : i + batch_size]
            # Forward pass
            outputs = model(x_batch)
            loss = criterion(outputs, y_batch)
            # Backward pass und Optimierung
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}")

    return model


# %% Modellbewertung und Visualisierung
def evaluate_and_forecast(model, x_test, y_test, scaler, test_dates, future_steps=10):
    model.eval()
    with torch.no_grad():
        # Generate predictions for the test set
        predictions = model(x_test).numpy()

    # Reverse scaling for test set predictions
    predictions = scaler.inverse_transform(predictions.reshape(-1, 1))
    y_test = scaler.inverse_transform(y_test.numpy().reshape(-1, 1))

    # Prepare future dates
    last_test_date = test_dates.iloc[-1]  # Extract the last date
    future_dates = [last_test_date + pd.Timedelta(days=i + 1) for i in range(future_steps)]

    # Initialize future input with the last available test data
    future_input = x_test[-1].numpy().reshape(1, -1, 1)  # Reshape to match LSTM input
    future_predictions = []

    for _ in range(future_steps):
        with torch.no_grad():
            future_pred = model(torch.tensor(future_input, dtype=torch.float32))
        future_pred_scaled = future_pred.numpy().reshape(-1, 1)  # Flatten prediction for inverse scaling
        future_pred = scaler.inverse_transform(future_pred_scaled)  # Reverse scale
        future_predictions.append(future_pred.item())

        # Update future input with the new prediction
        future_input = np.append(future_input[:, 1:, :], future_pred_scaled.reshape(1, 1, -1), axis=1)

    rmse = np.sqrt(np.mean((y_test - predictions) ** 2)).item()  # Convert RMSE to Python float

    # Combine dates with predictions
    predicted_values_with_dates = list(zip(test_dates.tolist(), predictions.flatten().tolist()))
    future_values_with_dates = list(zip(future_dates, future_predictions))

    return predicted_values_with_dates, y_test.flatten().tolist(), rmse, future_values_with_dates