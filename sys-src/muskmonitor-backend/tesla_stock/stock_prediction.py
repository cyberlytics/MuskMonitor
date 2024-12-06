# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler

# %%
sns.set_style("darkgrid")
plt.style.use("fivethirtyeight")

# %%
df = pd.read_json("konvertierte_datei.json")
# %%
df["Datum"] = pd.to_datetime(df["Datum"])

# %%
df["Year"] = df["Datum"].dt.year
df["Month"] = df["Datum"].dt.month

# %%
dataset = df[["close", "open", "high", "low", "volume"]]
dataset = pd.DataFrame(dataset)
data = dataset.values

# %%
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(dataset[["close"]].values)

# %%
train_size = int(len(data) * 0.75)  # 2217
test_size = len(data) - train_size  # 739

print("Train Size : ", train_size, "Test Size : ", test_size)

# %%
# Aufteilen in Trainings- und Testdaten
train_data = scaled_data[:train_size]
test_data = scaled_data[train_size - 60 :]

# %%
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i - 60 : i, 0])
    y_train.append(train_data[i, 0])

# %%
# Convert to PyTorch tensors
x_train = torch.tensor(x_train, dtype=torch.float32).unsqueeze(
    -1
)  # Shape: [batch, seq_len, 1]
y_train = torch.tensor(y_train, dtype=torch.float32).unsqueeze(-1)  # Shape: [batch, 1]


# %%
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
        out = out[:, -1, :]  # Use the last output of the sequence
        out = torch.relu(self.fc1(out))
        out = torch.relu(self.fc2(out))
        out = self.fc3(out)
        return out


# %%
# Model hyperparameters
input_size = 1
hidden_size = 50
output_size = 1
model = LSTMModel(input_size, hidden_size, output_size)

# Loss and optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# %%
# Training loop
epochs = 100
batch_size = 32

for epoch in range(epochs):
    model.train()
    for i in range(0, len(x_train), batch_size):
        x_batch = x_train[i : i + batch_size]
        y_batch = y_train[i : i + batch_size]

        # Forward pass
        outputs = model(x_batch)
        loss = criterion(outputs, y_batch)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}")

# %%
# Testdaten vorbereiten
x_test = []
y_test = []
for i in range(60, len(test_data)):
    x_test.append(test_data[i - 60 : i, 0])
    y_test.append(test_data[i, 0])

x_test = torch.tensor(x_test, dtype=torch.float32).unsqueeze(-1)
y_test = torch.tensor(y_test, dtype=torch.float32).unsqueeze(-1)
# %%
# Testing und Vorhersagen
model.eval()
with torch.no_grad():
    predictions = model(x_test).numpy()

# Rückwärtsskalierung
predictions = predictions.reshape(-1, 1)
predictions = scaler.inverse_transform(predictions)

y_test = y_test.numpy().reshape(-1, 1)
y_test = scaler.inverse_transform(y_test)

# Berechnung des RMSE
rmse = np.sqrt(np.mean((y_test - predictions) ** 2))
print(f"RMSE: {rmse:.2f}")
# %%
# Visualization
train = dataset.iloc[:train_size]
test = dataset.iloc[train_size:]
test["Predictions"] = predictions

plt.figure(figsize=(15, 6))
plt.title("TESLA Close Stock Price Prediction", fontsize=18)
plt.xlabel("Date", fontsize=18)
plt.ylabel("Close Price", fontsize=18)
plt.plot(train["close"], linewidth=3)
plt.plot(test["close"], linewidth=3)
plt.plot(test["Predictions"], linewidth=3)
plt.legend(["Train", "Test", "Predictions"])
plt.show()

# %%
