import pytest
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from tesla_stock.stock_prediction import (
    fetch_data_from_db,
    prepare_data,
    create_lstm_data,
    evaluate_and_forecast,
    LSTMModel,
)
from unittest.mock import MagicMock
from pymongo import MongoClient

@pytest.fixture
def sample_data():
    # Erstellen Sie eine Beispiel-Datenmenge
    data = {
        "Datum": pd.date_range(start="2020-01-01", periods=100, freq="D"),
        "close": np.random.rand(100),
        "open": np.random.rand(100),
        "high": np.random.rand(100),
        "low": np.random.rand(100),
        "volume": np.random.randint(1, 1000, size=100),
    }
    df = pd.DataFrame(data)
    return df


@pytest.fixture
def model():
    input_size = 1
    hidden_size = 50
    output_size = 1
    model = LSTMModel(input_size, hidden_size, output_size)
    return model


def test_data_preprocessing(sample_data):
    df = sample_data
    df["Datum"] = pd.to_datetime(df["Datum"])
    dataset = df[["close", "open", "high", "low", "volume"]]
    data = dataset.values

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset[["close"]].values)

    train_size = int(len(data) * 0.75)
    test_size = len(data) - train_size

    assert train_size == 75
    assert test_size == 25

    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size - 60 :]

    assert len(train_data) == 75
    assert len(test_data) == 85


def test_model_training(sample_data, model):
    df = sample_data
    df["Datum"] = pd.to_datetime(df["Datum"])
    dataset = df[["close", "open", "high", "low", "volume"]]
    data = dataset.values

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset[["close"]].values)

    train_size = int(len(data) * 0.75)
    train_data = scaled_data[:train_size]

    x_train = []
    y_train = []

    for i in range(60, len(train_data)):
        x_train.append(train_data[i - 60 : i, 0])
        y_train.append(train_data[i, 0])

    x_train = torch.tensor(x_train, dtype=torch.float32).unsqueeze(-1)
    y_train = torch.tensor(y_train, dtype=torch.float32).unsqueeze(-1)

    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    epochs = 10
    batch_size = 32

    for epoch in range(epochs):
        model.train()
        for i in range(0, len(x_train), batch_size):
            x_batch = x_train[i : i + batch_size]
            y_batch = y_train[i : i + batch_size]

            outputs = model(x_batch)
            loss = criterion(outputs, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    assert loss.item() < 1.0


def test_model_prediction(sample_data, model):
    df = sample_data
    df["Datum"] = pd.to_datetime(df["Datum"])
    dataset = df[["close", "open", "high", "low", "volume"]]
    data = dataset.values

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset[["close"]].values)

    train_size = int(len(data) * 0.75)
    test_data = scaled_data[train_size - 60 :]

    x_test = []
    y_test = []
    for i in range(60, len(test_data)):
        x_test.append(test_data[i - 60 : i, 0])
        y_test.append(test_data[i, 0])

    x_test = torch.tensor(x_test, dtype=torch.float32).unsqueeze(-1)
    y_test = torch.tensor(y_test, dtype=torch.float32).unsqueeze(-1)

    model.eval()
    with torch.no_grad():
        predictions = model(x_test).numpy()

    predictions = predictions.reshape(-1, 1)
    predictions = scaler.inverse_transform(predictions)

    y_test = y_test.numpy().reshape(-1, 1)
    y_test = scaler.inverse_transform(y_test)

    rmse = np.sqrt(np.mean((y_test - predictions) ** 2))
    assert rmse < 1.0

@pytest.fixture
def mock_mongo_data():
    return [
        {"Datum": "2023-01-01", "close": 100, "open": 95, "high": 105, "low": 90, "volume": 1000},
        {"Datum": "2023-01-02", "close": 102, "open": 100, "high": 106, "low": 98, "volume": 1100},
        {"Datum": "2023-01-03", "close": 101, "open": 98, "high": 104, "low": 97, "volume": 900},
    ]


def test_prepare_data(sample_data):
    train_data, test_data, scaler = prepare_data(sample_data)
    assert train_data.shape[0] < len(sample_data)
    assert len(test_data) > 0
    assert scaler is not None


def test_create_lstm_data():
    data = np.random.rand(100, 1)
    x_data, y_data = create_lstm_data(data, time_step=10)

    assert x_data.shape[0] == len(data) - 10
    assert y_data.shape[0] == len(data) - 10
    assert x_data.shape[1] == 10  # Time step


def test_evaluate_and_forecast(sample_data, model):
    train_data, test_data, scaler = prepare_data(sample_data)
    x_test, y_test = create_lstm_data(test_data)

    # Convert test_dates to a Series to be compatible with .iloc
    test_dates = pd.Series(pd.date_range("2023-01-01", periods=len(y_test)))

    model.eval()
    predicted, y_actual, rmse, future_forecast = evaluate_and_forecast(
        model, x_test, y_test, scaler, test_dates, future_steps=5
    )

    assert len(predicted) == len(y_actual)
    assert rmse > 0
    assert len(future_forecast) == 5
