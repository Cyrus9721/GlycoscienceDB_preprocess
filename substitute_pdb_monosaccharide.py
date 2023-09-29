import pandas as pd
import numpy as np
import os


def create_pdb_summary(dir, summary_name='pdb_name.csv'):
    """
    This method read all files end with '.pdb', and create a csv file that take their summary
    dir: directory where pdb files is stored
    :return: a csv file
    column1: directory: where the pdb files stored.
    column2: filename: name of the pdb file
    column3: formula: name of the formula inside the pdb file, missing formula files are labeled as 'Missing formula'
    """
    files = os.listdir(dir)
    dir_name = [f for f in files if '-2022' in f]

    glycan_name_list = []
    dir_list = []
    file_list = []
    for path_pdb in dir_name:

        files = os.listdir(path_pdb)
        files_pdb = [f for f in files if '.pdb' in f]
        for i in range(len(files_pdb)):
            with open(os.path.join(path_pdb, files_pdb[i])) as f:
                pdb_context = f.readlines()

                # missing formula is the second line does not contain formula
                if 'ATOM ' in pdb_context[1]:
                    glycan_names = 'Missing formula'
                else:
                    glycan_names = pdb_context[1].split('\n')[0]
                glycan_name_list.append(glycan_names)

                dir_list.append(path_pdb)
                file_list.append(files_pdb[i])

    df = pd.DataFrame([dir_list, file_list, glycan_name_list]).T
    df.columns = ['directory', 'filename', 'formula']
    df.to_csv(summary_name, index=False)


def substitute_id_by_monosaccharide(df, df_id, out_directory='data/directory_copy/'):
    """
    :param df: summary of pdb file output from 'create_pdb_summary'
    :param df_id: csv file where each row stores the monosaccharide corresponding the id
    :param out_directory: directory where the new pdb files output
    :return:
    """
    df_combined = pd.concat([df, df_id], axis=1)
    df_combined = df_combined.dropna(how='all', axis=1)
    for i in range(len(df_combined)):
        temp_directory = df_combined.loc[i].directory
        temp_filename = df_combined.loc[i].filename
        mono_id_list = df_combined.loc[i][3:].values
        mono_id_list = mono_id_list[~pd.isnull(mono_id_list)]
        with open(os.path.join(temp_directory, temp_filename)) as f:
            f = f.readlines()
            for j in range(len(f)):
                if 'UNTI' in f[j]:
                    temp_l = f[j]
                    substructure_id = temp_l.split()[4]
                    substructure_name = mono_id_list[int(substructure_id) - 1]
                    new_line = f[j].replace('UNTI', substructure_name)
                    f[j] = new_line
            with open(os.path.join(out_directory, temp_directory, temp_filename), 'w') as fw:
                for fw_l in f:
                    fw.write(fw_l)


def main():
    # for write out summary file
    # create_pdb_summary(dir='', summary_name='pdb_name.csv')

    # for create replace index id by actual monosaccharide
    # df = pd.read_csv('pdb_name.csv')
    # df_id = pd.read_csv('pdb_labeled.csv', header= None)
    # substitute_id_by_monosaccharide(df, df_id, out_directory='data/directory_copy/')
    pass


if __name__ == "__main__":
    main()
