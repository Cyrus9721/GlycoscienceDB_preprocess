import pandas as pd
import numpy as np
import os


def check_unti(path_pdb, file_name, UNTI='UNTI'):
    with open(os.path.join(path_pdb, file_name)) as f:
        f = f.readlines()
        f = f[2:-1]  # exclude glycan name etc
        fourthval = [i.split()[3] for i in f]
        num_total = len(fourthval)
        num_missing = np.sum(np.array(fourthval) == UNTI)
    return num_total, num_missing


def main():
    dir_list = []
    file_list = []
    missing_list = []
    total_list = []
    files = os.listdir()
    dir_name = [f for f in files if '-2022' in f]
    for path_pdb in dir_name:

        files = os.listdir(path_pdb)
        files_pdb = [f for f in files if '.pdb' in f]

        for file_name in files_pdb:
            temp_total, temp_missing = check_unti(path_pdb, file_name)

            dir_list.append(path_pdb)
            file_list.append(file_name)
            missing_list.append(temp_missing)
            total_list.append(temp_total)

    df_summary = pd.DataFrame([dir_list, file_list, missing_list, total_list]).T
    df_summary.columns = ['Directory name', 'PDB file name', 'Number of missing with UNTI', 'Number of rows']
    df_summary.to_csv('pdb_summary.csv', index=False)


if __name__ == "__main__":
    main()
