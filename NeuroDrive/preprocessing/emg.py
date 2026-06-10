import neurokit2 as nk
import mne
mne.set_log_level('error')
import json
from os.path import isfile

#corresponds to right calf, right calf, left arm, right arm
channels = ['EMG1', 'EMG2', 'EMG3', 'EMG4']

labels = ['turn', 'throttle', 'change', 'break']

root_dir = '/run/media/aaditya/DATA/Datasets/'

#subjects 1 through 5
for sub in range(1,6):
    for label in labels:
        in_file = root_dir + f'rawdata/additional/additiondrive/sub{sub}/{label}/EMG/data.bdf'
        out_dir = root_dir + f'intermediate/EMG/'

        print(f'reading {sub}_{label}.bdf')
        
        for channel in channels:
            out_file = f'{sub}_{label}_{channel}'

            file = mne.io.read_raw_bdf(in_file)
            df, di = nk.emg_process(file.get_data(channel)[0], sampling_rate=1000)

            df.to_csv(out_dir + out_file + '.csv', index=False)
            print(f'written {out_file}.csv')

            with open(out_dir + out_file + '.json', 'w') as file:
                di['EMG_Activity'] = di['EMG_Activity'].tolist()
                di['EMG_Onsets'] = di['EMG_Onsets'].tolist()
                di['EMG_Offsets'] = di['EMG_Offsets'].tolist()
                json.dump(di, file)
                print(f'written {out_file}.json')
            
        print('', sep='\n')
