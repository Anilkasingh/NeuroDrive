import numpy as np
from sklearn.model_selection import train_test_split
from numpy.fft import fft
from mne.io import read_epochs_eeglab
from scipy.stats import skew, kurtosis
from scipy.signal import welch, find_peaks
from antropy import spectral_entropy, hjorth_params


def get_label(epochs):
    """Extract trial labels"""
    true_label = []
    dic = {v: k for k, v in epochs.event_id.items()}
    for record in epochs.events:
        if dic[record[2]] in ['139', '141', '145']:  # brake
            true_label.append(0)
        elif dic[record[2]] in ['125', '127']:  # turn
            true_label.append(1)
        elif dic[record[2]] in ['129', '131']:  # change
            true_label.append(2)
        elif dic[record[2]] in ['137', '143']:  # throttle
            true_label.append(3)
        elif dic[record[2]] in ['133']:  # stable
            true_label.append(4)
    return true_label


# ---------- FEATURE EXTRACTION FUNCTIONS ----------
def extract_eeg_features(signal, sf=250):
    features = []
    features.append(np.mean(signal))
    features.append(np.std(signal))
    features.append(skew(signal))
    features.append(kurtosis(signal))
    features.append(np.ptp(signal))

    freqs, psd = welch(signal, sf, nperseg=sf*2)
    bands = {'delta': (0.5, 4), 'theta': (4, 8), 'alpha': (8, 12),
             'beta': (12, 30), 'gamma': (30, 45)}
    for band, (low, high) in bands.items():
        idx = np.logical_and(freqs >= low, freqs <= high)
        features.append(np.trapz(psd[idx], freqs[idx]))

    features.append(spectral_entropy(signal, sf, method='welch'))
    features.extend(hjorth_params(signal))  # activity, mobility, complexity
    return features


def extract_ecg_features(signal, sf=250):
    features = []
    peaks, _ = find_peaks(signal, distance=sf*0.6)
    if len(peaks) > 1:
        rr_intervals = np.diff(peaks) / sf
        features.append(np.mean(rr_intervals))
        features.append(np.std(rr_intervals))
        features.append(np.sqrt(np.mean(np.square(np.diff(rr_intervals)))))  # RMSSD
    else:
        features.extend([0, 0, 0])
    return features


def extract_emg_features(signal):
    features = []
    features.append(np.mean(np.abs(signal)))
    features.append(np.sqrt(np.mean(signal**2)))  # RMS
    features.append(np.var(signal))
    features.append(np.sum(np.abs(np.diff(signal))))
    return features


def extract_gsr_features(signal):
    features = []
    features.append(np.mean(signal))
    features.append(np.std(signal))
    features.append(np.max(signal) - np.min(signal))
    features.append(np.median(signal))
    return features


# ---------- DATA LOADING & FEATURE EXTRACTION ----------
def data_preprocess():
    datapath = '/Users/anilkasingh/preprocessed data/'

    DATA, y = [], []

    for subj in range(1, 31):
        # Load each modality
        EEG_temp = read_epochs_eeglab(datapath + f'EEG/EEG_{subj}.set')
        ECG_temp = read_epochs_eeglab(datapath + f'ECG/ECG_{subj}.set')
        EMG_temp = read_epochs_eeglab(datapath + f'EMG/EMG_{subj}.set')

        EEG = EEG_temp.get_data()
        ECG = ECG_temp.get_data()
        EMG = EMG_temp.get_data()

        # Align trial count across modalities
        n_trials = min(len(EEG), len(ECG), len(EMG))
        labels = get_label(EEG_temp)[:n_trials]

        for trial_idx in range(n_trials):
            features_trial = []

            # EEG features (all channels)
            for ch in range(EEG.shape[1]):
                features_trial.extend(extract_eeg_features(EEG[trial_idx, ch, :], sf=250))

            # ECG features
            for ch in range(ECG.shape[1]):
                features_trial.extend(extract_ecg_features(ECG[trial_idx, ch, :], sf=250))

            # EMG features
            for ch in range(EMG.shape[1]):
                features_trial.extend(extract_emg_features(EMG[trial_idx, ch, :]))

            DATA.append(features_trial)
            y.append(labels[trial_idx])

    DATA = np.array(DATA)
    y = np.array(y)

    return train_test_split(DATA, y, test_size=0.2, random_state=42)



if __name__ == "__main__":
    X_train, X_test, y_train, y_test = data_preprocess()
    print("Feature matrix shape:", X_train.shape)
    print("Labels shape:", y_train.shape)
