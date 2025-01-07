import pytest
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from tesla_stock.stock_prediction import LSTMModel


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
