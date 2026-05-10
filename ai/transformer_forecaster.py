import numpy as np
import pandas as pd

from tensorflow.keras.models import Model

from tensorflow.keras.layers import (

    Input,
    Dense,
    LayerNormalization,
    MultiHeadAttention,
    GlobalAveragePooling1D
)

from sklearn.preprocessing import (
    MinMaxScaler
)

# =========================================================
# PREPARE DATA
# =========================================================

def prepare_sequences(

    prices,

    sequence_length=20
):

    scaler = MinMaxScaler()

    scaled = scaler.fit_transform(

        prices.values.reshape(-1, 1)
    )

    X = []
    y = []

    for i in range(

        sequence_length,

        len(scaled)
    ):

        X.append(

            scaled[

                i-sequence_length:i
            ]
        )

        y.append(

            scaled[i]
        )

    X = np.array(X)

    y = np.array(y)

    return X, y, scaler

# =========================================================
# BUILD TRANSFORMER
# =========================================================

def build_transformer(

    input_shape
):

    inputs = Input(

        shape=input_shape
    )

    attention = MultiHeadAttention(

        num_heads=2,

        key_dim=8
    )(inputs, inputs)

    x = LayerNormalization()(

        attention + inputs
    )

    x = GlobalAveragePooling1D()(x)

    outputs = Dense(1)(x)

    model = Model(

        inputs,

        outputs
    )

    model.compile(

        optimizer="adam",

        loss="mse"
    )

    return model

# =========================================================
# TRAIN MODEL
# =========================================================

def train_transformer(

    prices
):

    X, y, scaler = prepare_sequences(

        prices
    )

    model = build_transformer(

        (X.shape[1], X.shape[2])
    )

    model.fit(

        X,

        y,

        epochs=2,

        batch_size=16,

        verbose=0
    )

    prediction = model.predict(

        X[-1:]

    )[0][0]

    prediction = scaler.inverse_transform(

        [[prediction]]
    )[0][0]

    return {

        "Model":

            model,

        "Prediction":

            prediction
    }