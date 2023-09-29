import numpy as np
import pandas as pd
import os
from tqdm import tqdm


class align_pdb_csv:
    """
    Align the labels of Carbon and Hydrogen
    Create new csv files for graph construction
    """
    def __init__(self, pdb_dir_list='data/directory_reformulate/', label_dir_list='data/directory_reformulate_labels/',
                 aligned_directory='data/directory_reformulate_combined'):
        self.pdb_dir_list = pdb_dir_list
        self.label_dir_list = label_dir_list
        self.aligned_directory = aligned_directory
        self.carbon_list = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        self.hydrogen_list_1_6 = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']
        self.hydrogen_6162_list = ['H61', 'H62']


    @staticmethod
    def check_illegal_hydrogen(df, df_name):
        max_residual = np.max(df['residual'].values)
        for i in range(1, max_residual + 1, 1):
            residual_df = df.loc[df['residual'] == i]
            atom_type_residual_df = residual_df['Atom_Type'].values
            if ('H6' in atom_type_residual_df) and ('H61' in atom_type_residual_df) and ('H62' in atom_type_residual_df):
                print(df_name, 'on residual', i, 'has vague Hydrogen, H6, H61, H62 appears at the same time')

            elif ('H6' in atom_type_residual_df) and ('H61' in atom_type_residual_df) and ('H62' not in atom_type_residual_df):
                print(df_name, 'on residual', i, 'has vague Hydrogen, H6, H61, appears at the same time')

            elif ('H6' in atom_type_residual_df) and ('H61' not in atom_type_residual_df) and ('H62' in atom_type_residual_df):
                print(df_name, 'on residual', i, 'has vague Hydrogen, H6, H62, appears at the same time')

            elif ('H6' not in atom_type_residual_df) and ('H61' in atom_type_residual_df) and ('H62' not in atom_type_residual_df):
                print(df_name, 'on residual', i, 'has vague Hydrogen, H61, appears but H62 missing')

            elif ('H6' in atom_type_residual_df) and ('H61' not in atom_type_residual_df) and ('H62' in atom_type_residual_df):
                print(df_name, 'on residual', i, 'has vague Hydrogen, H62, appears but H61 missing')

            elif ('H6' not in atom_type_residual_df) and ('H61' not in atom_type_residual_df) and ('H62' not in atom_type_residual_df):
                print(df_name, 'on residual', i, 'has vague Hydrogen, Missing all H6')

    def align_carbon_hydrogen(self):
        files = os.listdir(self.pdb_dir_list)
        files2 = os.listdir(self.label_dir_list)
        for f in tqdm(files2):

            """
            Ignore high shift data
            """
            if 'DGlcpAb1-3DGlcpNAcb1-OME.csv' in f:
                continue

            if 'DGlcpNAcb1-6(DGlcpNAcb1-4)(DGlcpNAcb1-3)DGlcpNAcb1-OME.csv' in f:
                continue

            f1 = f.replace('.csv', '.pdb.csv')
            temp_pdb_file = pd.read_csv(os.path.join(self.pdb_dir_list, f1))
            temp_label_file = pd.read_csv(os.path.join(self.label_dir_list, f))

            temp_label_column = temp_label_file.columns

            if f == 'LRhapa1-OME.csv':
                orig_atom_type = temp_pdb_file['Atom_Type'].copy()
                changed_index = np.where(orig_atom_type == 'H16')[0]
                orig_atom_type[changed_index] = 'H6'
                temp_pdb_file['Atom_Type'] = orig_atom_type

        #     check_illegal_hydrogen(temp_pdb_file, f1)

            temp_labels = np.repeat(-1.0, len(temp_pdb_file))

            for i in range(len(temp_pdb_file)):
                current_atom_type = temp_pdb_file.loc[i, ['Atom_Type']].values[0]
                current_residual = temp_pdb_file.loc[i, ['residual']].values[0]

                if current_atom_type in self.carbon_list:

                    current_corresponding_columns_in_label = current_atom_type.split('C')[1] + '.0'

                    temp_labels[i] = temp_label_file.loc[int(current_residual * 2-2),
                                                     [current_corresponding_columns_in_label]].values[0]

                elif current_atom_type in self.hydrogen_6162_list:
                    if f1 == 'LRhapa1-OME.pdb.csv':
                        print(f, 'has vague Hydrogen labels skipping labels of H61, H62')

                    elif current_atom_type == 'H61':
                        current_corresponding_columns_in_label = '6.0'
                        temp_labels[i] = temp_label_file.loc[int(current_residual * 2-1),
                                                     [current_corresponding_columns_in_label]].values[0]
                    else:
                        current_corresponding_columns_in_label = '6.0.1'
                        temp_labels[i] = temp_label_file.loc[int(current_residual * 2-1),
                                                     [current_corresponding_columns_in_label]].values[0]

                # this should be the last since we want
                elif current_atom_type in self.hydrogen_list_1_6:
                    current_corresponding_columns_in_label = current_atom_type.split('H')[1] + '.0'
                    temp_labels[i] = temp_label_file.loc[int(current_residual * 2-1),
                                                     [current_corresponding_columns_in_label]].values[0]
            temp_pdb_file['labels'] = temp_labels
            temp_pdb_file.to_csv('data/directory_reformulate_combined/' + f, index = False)



def main():
    A = align_pdb_csv()
    A.align_carbon_hydrogen()

    # Some later-found issues
    # this is for vague H data, set H61, H62 to -1 since H6 exists in the data
    temp_df_modified = pd.read_csv('data/directory_reformulate_combined/LFucpb1-3DGlcpNAcb1-OME.csv')
    temp_df_modified_labels = temp_df_modified['labels'].values
    temp_df_modified_labels[-1] = -1.00
    temp_df_modified_labels[-2] = -1.00
    temp_df_modified['labels'] = temp_df_modified_labels
    temp_df_modified.to_csv('data/directory_reformulate_combined/LFucpb1-3DGlcpNAcb1-OME.csv', index = False)

    # this is for high shift data but only on one atom (C6) we ignore them, substitute to -1.
    # DGlcpAb1-6DGalpb1-OME.csv 176.27
    # DGlcpAb1-3DGalpb1-OME.csv 176.34
    # DGlcpAb1-OME.csv 176.52
    # DGlcpAa1-OME.csv 177.15
    temp_df_modified = pd.read_csv('data/directory_reformulate_combined/DGlcpAb1-6DGalpb1-OME.csv')
    temp_df_modified_labels = temp_df_modified['labels'].values
    temp_df_modified_labels[31] = -1.00
    temp_df_modified['labels'] = temp_df_modified_labels
    temp_df_modified.to_csv('data/directory_reformulate_combined/DGlcpAb1-6DGalpb1-OME.csv', index = False)


    temp_df_modified = pd.read_csv('data/directory_reformulate_combined/DGlcpAb1-3DGalpb1-OME.csv')
    temp_df_modified_labels = temp_df_modified['labels'].values
    temp_df_modified_labels[31] = -1.00
    temp_df_modified['labels'] = temp_df_modified_labels
    temp_df_modified.to_csv('data/directory_reformulate_combined/DGlcpAb1-3DGalpb1-OME.csv', index = False)

    temp_df_modified = pd.read_csv('data/directory_reformulate_combined/DGlcpAb1-OME.csv')
    temp_df_modified_labels = temp_df_modified['labels'].values
    temp_df_modified_labels[5] = -1.00
    temp_df_modified['labels'] = temp_df_modified_labels
    temp_df_modified.to_csv('data/directory_reformulate_combined/DGlcpAb1-OME.csv', index = False)

    temp_df_modified = pd.read_csv('data/directory_reformulate_combined/DGlcpAa1-OME.csv')
    temp_df_modified_labels = temp_df_modified['labels'].values
    temp_df_modified_labels[5] = -1.00
    temp_df_modified['labels'] = temp_df_modified_labels
    temp_df_modified.to_csv('data/directory_reformulate_combined/DGlcpAa1-OME.csv', index = False)


if __name__ == "__main__":
    main()
