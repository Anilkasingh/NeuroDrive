# # deep_pipeline_raw.py
# # ---------------------------------------------------------
# # EEG Deep Learning Pipeline using raw EEG sequences
# # LSTM and GRU models trained sequentially with full evaluation
# # ---------------------------------------------------------

# import torch
# import torch.nn as nn
# import torch.optim as optim
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
# from main import read_epochs_eeglab, get_label  # We'll load raw EEG
# import numpy as np
# from sklearn.preprocessing import StandardScaler
# import collections

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # ---------------------- Data Loading ----------------------
# def load_raw_eeg_data(subjects=range(1, 31), sf=250):
#     """
#     Loads raw EEG sequences for all subjects
#     Returns: X (N_trials, timesteps, channels), y (labels)
#     """
#     datapath = '/Users/anilkasingh/preprocessed data/'
#     X_all, y_all = [], []

#     for subj in subjects:
#         EEG_temp = read_epochs_eeglab(datapath + f'EEG/EEG_{subj}.set')
#         EEG_data = EEG_temp.get_data()  # shape: (trials, channels, timesteps)
#         labels = get_label(EEG_temp)
#         n_trials = EEG_data.shape[0]

#         X_all.append(EEG_data[:n_trials])
#         y_all.extend(labels[:n_trials])

#     X_all = np.concatenate(X_all, axis=0)  # (total_trials, channels, timesteps)
#     y_all = np.array(y_all)

#     # Reorder to (trials, timesteps, channels)
#     X_all = np.transpose(X_all, (0, 2, 1))

#     # Normalize per channel
#     N, T, C = X_all.shape
#     X_flat = X_all.reshape(-1, C)
#     scaler = StandardScaler()
#     X_flat = scaler.fit_transform(X_flat)
#     X_all = X_flat.reshape(N, T, C)

#     return torch.tensor(X_all, dtype=torch.float32), torch.tensor(y_all, dtype=torch.long)

# # Split train/test
# from sklearn.model_selection import train_test_split
# X, y = load_raw_eeg_data()
# x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# print("Class distribution in train:", collections.Counter(y_train.numpy()))
# print("Class distribution in test:", collections.Counter(y_test.numpy()))

# # ---------------------- LSTM Model ------------------------
# class EEG_LSTM(nn.Module):
#     def __init__(self, input_size, hidden_size=128, num_layers=2, num_classes=5, dropout=0.3):
#         super(EEG_LSTM, self).__init__()
#         self.lstm = nn.LSTM(input_size, hidden_size, num_layers=num_layers,
#                             batch_first=True, dropout=dropout)
#         self.fc = nn.Sequential(
#             nn.Linear(hidden_size, 64),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(64, num_classes)
#         )

#     def forward(self, x):
#         out, _ = self.lstm(x)
#         out = out[:, -1, :]
#         out = self.fc(out)
#         return out

# # ---------------------- GRU Model -------------------------
# class EEG_GRU(nn.Module):
#     def __init__(self, input_size, hidden_size=128, num_layers=2, num_classes=5, dropout=0.3):
#         super(EEG_GRU, self).__init__()
#         self.gru = nn.GRU(input_size, hidden_size, num_layers=num_layers,
#                           batch_first=True, dropout=dropout)
#         self.fc = nn.Sequential(
#             nn.Linear(hidden_size, 64),
#             nn.ReLU(),
#             nn.Dropout(0.3),
#             nn.Linear(64, num_classes)
#         )

#     def forward(self, x):
#         out, _ = self.gru(x)
#         out = out[:, -1, :]
#         out = self.fc(out)
#         return out

# # ---------------------- Training Function -----------------
# def train_model(model, x_train, y_train, x_test, y_test, epochs=50, lr=5e-4, patience=8):
#     model = model.to(device)
#     from sklearn.utils.class_weight import compute_class_weight

#     y_train_np = y_train.cpu().numpy()
#     classes = np.unique(y_train_np)
#     class_weights = compute_class_weight('balanced', classes=classes, y=y_train_np)
#     class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32).to(device)

#     criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
#     optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
#     scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3, verbose=True)

#     best_f1, patience_counter, best_state = 0, 0, None

#     for epoch in range(epochs):
#         model.train()
#         optimizer.zero_grad()
#         outputs = model(x_train.to(device))
#         loss = criterion(outputs, y_train.to(device))
#         loss.backward()
#         optimizer.step()

#         model.eval()
#         with torch.no_grad():
#             preds = model(x_test.to(device))
#             preds = torch.argmax(preds, dim=1).cpu().numpy()
#         y_true = y_test.cpu().numpy()
#         f1 = f1_score(y_true, preds, average='weighted', zero_division=0)
#         scheduler.step(f1)

#         if f1 > best_f1:
#             best_f1 = f1
#             best_state = model.state_dict()
#             patience_counter = 0
#         else:
#             patience_counter += 1

#         if (epoch + 1) % 5 == 0 or epoch == 0:
#             print(f"Epoch [{epoch+1}/{epochs}] | Loss: {loss.item():.4f} | F1: {f1:.4f} | LR: {optimizer.param_groups[0]['lr']:.6f}")

#         if patience_counter >= patience:
#             print(f"⏹️ Early stopping at epoch {epoch+1}")
#             break

#     if best_state:
#         model.load_state_dict(best_state)

#     model.eval()
#     with torch.no_grad():
#         preds = model(x_test.to(device))
#         preds = torch.argmax(preds, dim=1).cpu().numpy()

#     y_true = y_test.cpu().numpy()

#     acc = accuracy_score(y_true, preds)
#     prec = precision_score(y_true, preds, average='weighted', zero_division=0)
#     rec = recall_score(y_true, preds, average='weighted', zero_division=0)
#     f1 = f1_score(y_true, preds, average='weighted', zero_division=0)

#     print("\nClassification Report:\n", classification_report(y_true, preds, zero_division=0))
#     print("Confusion Matrix:\n", confusion_matrix(y_true, preds))
#     print(f"✅ Accuracy: {acc:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")

#     return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1}

# # ---------------------- Main ------------------------------
# input_size = x_train.shape[2]
# num_classes = len(np.unique(y_train.numpy()))

# print("\n🚀 Training LSTM on raw EEG...")
# lstm_model = EEG_LSTM(input_size=input_size, num_classes=num_classes)
# lstm_results = train_model(lstm_model, x_train, y_train, x_test, y_test)

# print("\n🚀 Training GRU on raw EEG...")
# gru_model = EEG_GRU(input_size=input_size, num_classes=num_classes)
# gru_results = train_model(gru_model, x_train, y_train, x_test, y_test)

# # ---------------------- Compare ---------------------------
# print("\n📊 Model Comparison Summary:")
# print(f"LSTM → Accuracy: {lstm_results['accuracy']:.4f}, F1: {lstm_results['f1']:.4f}")
# print(f"GRU  → Accuracy: {gru_results['accuracy']:.4f}, F1: {gru_results['f1']:.4f}")

# if lstm_results["f1"] > gru_results["f1"]:
#     print("\n🏆 Best Model: LSTM")
# else:
#     print("\n🏆 Best Model: GRU")
# =========================================================
# EEG Classification with GRU & LSTM (Optimized Channels)
# =========================================================
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping
from mne.io import read_epochs_eeglab

# -------------------------------
# 1. Label Extraction
# -------------------------------
def get_label(epochs):
    labels = []
    mapping = {v: k for k, v in epochs.event_id.items()}
    for event in epochs.events:
        code = mapping[event[2]]
        if code in ['139', '141', '145']:  # brake
            labels.append(0)
        elif code in ['125', '127']:  # turn
            labels.append(1)
        elif code in ['129', '131']:  # change
            labels.append(2)
        elif code in ['137', '143']:  # throttle
            labels.append(3)
        elif code in ['133']:  # stable
            labels.append(4)
    return labels


# -------------------------------
# 2. Helper Function
# -------------------------------
def find_class_index(label, c):
    return [i for i, l in enumerate(label) if l == c]


# -------------------------------
# 3. Preprocessing
# -------------------------------
def data_preprocess():
    datapath = '/Users/anilkasingh/preprocessed data/'
    all_data, all_labels = [], []

    for subj in range(1, 31):
        EEG = read_epochs_eeglab(datapath + f'EEG/EEG_{subj}.set')
        EEG.pick_types(eeg=True)  # keep all EEG channels
        data = EEG.get_data()     # (n_epochs, n_channels, n_times)
        labels = get_label(EEG)
        all_data.append(data)
        all_labels.extend(labels)

    DATA = np.concatenate(all_data, axis=0)
    y = np.array(all_labels)

    # normalize per channel
    for i in range(DATA.shape[1]):
        scaler = StandardScaler()
        DATA[:, i, :] = scaler.fit_transform(DATA[:, i, :])

    print(f"Final data shape: {DATA.shape}")
    return train_test_split(DATA, y, test_size=0.2, random_state=42, stratify=y)


# -------------------------------
# 4. GRU Model
# -------------------------------
def build_gru_model(input_shape, num_classes):
    model = Sequential([
        GRU(128, return_sequences=True, input_shape=input_shape),
        Dropout(0.3),
        GRU(64),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model


# -------------------------------
# 5. Main Script
# -------------------------------
if __name__ == "__main__":
    x_train, x_test, y_train, y_test = data_preprocess()

    # transpose for RNN: (samples, time, features)
    x_train_rnn = np.transpose(x_train, (0, 2, 1))
    x_test_rnn = np.transpose(x_test, (0, 2, 1))

    y_train_oh = to_categorical(y_train, 5)
    y_test_oh = to_categorical(y_test, 5)

    model = build_gru_model((x_train_rnn.shape[1], x_train_rnn.shape[2]), 5)
    model.summary()

    es = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(
        x_train_rnn, y_train_oh,
        validation_split=0.2,
        epochs=80,
        batch_size=64,
        callbacks=[es],
        verbose=1
    )

    loss, acc = model.evaluate(x_test_rnn, y_test_oh)
   
