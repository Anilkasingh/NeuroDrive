
from main import data_preprocess  # must return: x_train, x_test, y_train, y_test
import numpy as np
import pandas as pd

# Sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

# Keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, LSTM, Dense, Dropout, Conv1D, MaxPooling1D
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adamax
from tensorflow.keras.callbacks import EarlyStopping

# Visualization
import seaborn as sns
import matplotlib.pyplot as plt


# =========================================================
# Helper Functions
# =========================================================
def normalize_eeg_data(X):
    """Normalize each EEG channel separately."""
    X_norm = np.zeros_like(X)
    for i in range(X.shape[1]):
        scaler = StandardScaler()
        X_norm[:, i, :] = scaler.fit_transform(X[:, i, :])
    return X_norm


def evaluate_model(y_true, y_pred, model_name="Model"):
    """Unified evaluation with metrics + confusion matrix."""
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro')
    weighted_f1 = f1_score(y_true, y_pred, average='weighted')

    print(f"\n=== {model_name} Evaluation ===")
    print(f"Accuracy:     {acc:.4f}")
    print(f"Macro F1:     {macro_f1:.4f}")
    print(f"Weighted F1:  {weighted_f1:.4f}")
    print("\nDetailed classification report:\n")
    print(classification_report(y_true, y_pred, digits=4))

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f"{model_name} - Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.show()

    return {"Model": model_name, "Accuracy": acc, "Macro F1": macro_f1, "Weighted F1": weighted_f1}


# =========================================================
# Deep Learning Models (GRU / LSTM / GRU+CNN)
# =========================================================
def build_gru_model(input_shape, num_classes):
    model = Sequential([
        GRU(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        GRU(32),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer=Adamax(learning_rate=1e-3),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def build_lstm_model(input_shape, num_classes):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        LSTM(32),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer=Adamax(learning_rate=1e-3),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def build_gru_cnn_model(input_shape, num_classes):
    model = Sequential([
        Conv1D(64, 3, activation='relu', input_shape=input_shape),
        MaxPooling1D(2),
        GRU(64, return_sequences=True),
        GRU(32),
        Dense(16, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer=Adamax(learning_rate=1e-3),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


def train_rnn_model(model_fn, x_train, y_train, x_test, y_test,
                    epochs=100, batch_size=64):
    num_classes = int(np.max(y_train)) + 1
    y_train_oh = to_categorical(y_train, num_classes)
    y_test_oh  = to_categorical(y_test, num_classes)

    # Normalize EEG data
    x_train = normalize_eeg_data(x_train)
    x_test  = normalize_eeg_data(x_test)

    # Transpose (N, C, T) → (N, T, C)
    x_train_rnn = np.transpose(x_train, (0, 2, 1))
    x_test_rnn  = np.transpose(x_test, (0, 2, 1))

    model = model_fn(x_train_rnn.shape[1:], num_classes)

    es = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    history = model.fit(x_train_rnn, y_train_oh, validation_split=0.2,
                        epochs=epochs, batch_size=batch_size,
                        callbacks=[es], verbose=1)

    preds = model.predict(x_test_rnn)
    y_pred = np.argmax(preds, axis=1)
    y_true = np.argmax(y_test_oh, axis=1)
    res = evaluate_model(y_true, y_pred, model_fn.__name__.replace("build_", "").upper())

    # Optional: plot learning curves
    plt.figure(figsize=(8,4))
    plt.plot(history.history['accuracy'], label='Train Acc')
    plt.plot(history.history['val_accuracy'], label='Val Acc')
    plt.title(f'{model_fn.__name__.replace("build_", "").upper()} Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()

    return res


# =========================================================
# Main
# =========================================================
def main():
    all_results = []

    # Load data
    x_train, x_test, y_train, y_test = data_preprocess()
    print(f"Train: {x_train.shape}, Test: {x_test.shape}, Classes: {len(set(y_train))}")

    # GRU model
    res_gru = train_rnn_model(build_gru_model, x_train, y_train, x_test, y_test)
    all_results.append(res_gru)

    # LSTM model
    res_lstm = train_rnn_model(build_lstm_model, x_train, y_train, x_test, y_test)
    all_results.append(res_lstm)

    # GRU+CNN hybrid
    res_hybrid = train_rnn_model(build_gru_cnn_model, x_train, y_train, x_test, y_test)
    all_results.append(res_hybrid)

    # Final comparison table
    df = pd.DataFrame(all_results)
    print("\n============================")
    print("📊 Final Model Comparison")
    print("============================")
    print(df.to_string(index=False))

    plt.figure(figsize=(7,4))
    sns.barplot(x="Model", y="Accuracy", data=df)
    plt.title("Model Accuracy Comparison")
    plt.show()


if __name__ == "__main__":
    main()

