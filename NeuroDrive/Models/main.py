import numpy as np
from sklearn.model_selection import train_test_split
from numpy.fft import fft
from mne.io import concatenate_raws, read_raw_edf, read_epochs_eeglab


def get_label(epochs):
    true_label = []
    dic = {v: k for k, v in epochs.event_id.items()}
    test = epochs.events[:, -1]
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


def find_class_index(label, c):
    y = []
    for i in range(len(label)):
        if label[i] == c:
            y.append(i)
    return y


def data_preprocess():
    datapath = '/Users/anilkasingh/preprocessed data/'
    

    # Step 1: find total number of samples
    total_samples = 0
    for subj in range(1, 31):
        EEG_temp = read_epochs_eeglab(datapath + f'EEG/EEG_{subj}.set')
        label_EEG = get_label(EEG_temp)
        for class_idx in range(5):
            total_samples += len(find_class_index(label_EEG, class_idx))

    print(f"Total samples found: {total_samples}")

    # Step 2: initialize array properly
    DATA = np.zeros(shape=(total_samples, 2, 2000))
    y = []
    pointer = 0

    for subj in range(1, 31):
        EEG_temp = read_epochs_eeglab(datapath + f'EEG/EEG_{subj}.set')
        EEG_temp.pick_channels(['Fp1', 'Fp2'])


        EEG = EEG_temp.get_data()
        label_EEG = get_label(EEG_temp)

        for class_idx in range(5):
            class_indices = find_class_index(label_EEG, class_idx)
            for j in class_indices:
                sample = EEG[j, :, :]
                DATA[pointer, :, :] = sample
                y.append(class_idx)
                pointer += 1

    DATA = np.abs(fft(DATA))

    return train_test_split(DATA, y, test_size=0.2, random_state=35)



if __name__ == "__main__":
    data_preprocess()
    