import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential

# =========================================================
# DATA PREPARATION
# =========================================================


def prepare_sequences(prices, sequence_length=20):

    scaler = MinMaxScaler()

    scaled = scaler.fit_transform(prices.values.reshape(-1, 1))

    X = []
    y = []

    for i in range(sequence_length, len(scaled)):
        X.append(scaled[i - sequence_length : i])

        y.append(scaled[i])

    X = np.array(X)

    y = np.array(y)

    return X, y, scaler


# =========================================================
# BUILD MODEL
# =========================================================


def build_lstm(input_shape):

    model = Sequential()

    model.add(LSTM(50, return_sequences=False, input_shape=input_shape))

    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mse")

    return model


# =========================================================
# TRAIN MODEL
# =========================================================


def train_lstm(prices):

    X, y, scaler = prepare_sequences(prices)

    model = build_lstm((X.shape[1], X.shape[2]))

    model.fit(X, y, epochs=5, batch_size=16, verbose=0)

    prediction = model.predict(X[-1:])[0][0]

    prediction = scaler.inverse_transform([[prediction]])[0][0]

    return {"Model": model, "Prediction": prediction}
