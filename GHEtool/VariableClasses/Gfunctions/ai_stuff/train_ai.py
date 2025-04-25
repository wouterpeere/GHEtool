import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split

print("TensorFlow version:", tf.__version__)


def create_split_data():
    """spilt data for training and testing"""
    data = pd.read_feather("results_training_diff_fields.feather")
    normalize_vec = np.array((1 / 20, 1 / 20, 1 / 9, 1 / 9, 1 / 1000, 1 / 100, 1 / 0.4, 1 / (10**-6), 1 / 6, 1))

    x_train = data.iloc[::1, :10].to_numpy() * normalize_vec
    for i in reversed(range(1, 87)):
        data[f"result_{i}"] = data[f"result_{i}"] - data[f"result_{i - 1}"]

    y_train = data.iloc[::1, 10:].to_numpy()  # /1000
    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=0.2, random_state=40)

    pd.DataFrame(np.column_stack((x_test, y_test)), columns=data.columns).to_feather("results_test_data_diff_fields.feather")
    pd.DataFrame(np.column_stack((x_train, y_train)), columns=data.columns).to_feather("results_train_data_diff_fields.feather")


def main():
    """train neural network"""
    epochs = 20_000
    runs = 5
    batch_size = 512 * 10
    train_data = pd.read_feather("results_train_data_diff_fields.feather")
    x_train = train_data.iloc[:, :9].to_numpy()
    y_train = train_data.iloc[:, 10:].to_numpy()
    combined_dataset = tf.data.Dataset.from_tensor_slices((tf.cast(x_train, tf.float64), tf.cast(y_train, tf.float64)))
    combined_dataset = combined_dataset.shuffle(buffer_size=len(combined_dataset), reshuffle_each_iteration=True)
    combined_dataset = combined_dataset.repeat(10)  # epochs)
    combined_dataset = combined_dataset.prefetch(buffer_size=tf.data.AUTOTUNE)
    combined_dataset = combined_dataset.batch(batch_size)
    combined_dataset = combined_dataset.cache()
    test_data = pd.read_feather("results_test_data_diff_fields.feather")
    x_test = test_data.iloc[:, :9].to_numpy()
    y_test = test_data.iloc[:, 10:].to_numpy()

    variations = [{"layers": [128, 64]}]
    model = tf.keras.models.Sequential()
    model.add(tf.keras.layers.Dense(256, input_shape=(9,), activation="relu"))
    model.add(tf.keras.layers.Dense(64, activation="relu"))
    model.add(tf.keras.layers.Dense(87, activation="relu"))
    init_epoch = 0
    for _ in range(runs):
        optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
        model.compile(
            optimizer=optimizer,
            loss="mse",
            metrics=["mae", tf.keras.losses.Huber(delta=1), "mse", tf.keras.losses.MeanAbsolutePercentageError()],
        )
        history = model.fit(combined_dataset, epochs=init_epoch + epochs // 10 + 1, initial_epoch=init_epoch)
        model.compile(optimizer=optimizer, loss="mae", metrics=["mae", tf.keras.losses.Huber(delta=1), "mse", tf.keras.losses.MeanAbsolutePercentageError()])  #

        history = model.fit(combined_dataset, epochs=history.epoch[-1] + epochs // 10 + 1, initial_epoch=history.epoch[-1])  # , batch_size=batch_size)
        init_epoch = history.epoch[-1]

    result = model.evaluate(x_test, y_test, batch_size=512 * 10) * 1000
    variations[0]["mae"] = result[0]
    variations[0]["Huber"] = result[1]
    variations[0]["mse"] = result[2]
    variations[0]["MAPE"] = result[3]

    # Convert the weights to pandas DataFrames
    model_weights = model.get_weights()
    weights_dfs = [pd.DataFrame(weights if isinstance(weights, np.ndarray) else [weights]) for weights in model_weights]

    # Save each DataFrame to a CSV file
    for i, df in enumerate(weights_dfs):
        df.to_csv(f"layer_{i}_weights_diff_fields.csv", index=False, sep=";")


if __name__ == "__main__":  # pragma: no cover
    create_split_data()
    main()
