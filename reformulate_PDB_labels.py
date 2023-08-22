# @Author  : Zizhang Chen
# @Contact : zizhang2@outlook.com
import numpy as np
import pandas as pd
import os
from tqdm import tqdm


class Reformulate_pdb_csv:
    def __init__(self, pdb_dir_list='data/directory_copy/', pdb_dir_out_list='data/directory_reformulate/',
                 shift_labels_dir_out_list='data/directory_reformulate_labels/', pdb_columns=8):
        self.pdb_dir_list = pdb_dir_list
        self.pdb_dir_out_list = pdb_dir_out_list
        self.shift_labels_dir_out_list = shift_labels_dir_out_list
        self.pdb_columns = pdb_columns
        self.pdb_missing_formula = ['DManpb1-OME.pdb',
                                    'DGalpb1-OME.pdb',
                                    'DManpa1-OME.pdb',
                                    'DGlcpa1-OME.pdb',
                                    'DGalpa1-OME.pdb',
                                    'DGlcpb1-OME.pdb']

    def convert_singe_pdb_line(self, pdb_line):
        """
        :param pdb_line: a single line in pdb
        :return: dataframe-like rows with columns in need
        """
        out_list = pdb_line.split(' ')
        pdb_condense_line = [i for i in out_list if i != '']
        return pdb_condense_line[:self.pdb_columns]

    def sort_an_array(self, arr):
        pass

    def read_single_pdb(self, single_pdb, out_directory):
        """
        :param single_pdb: directory of a single pdb file
        :param out_directory: directory of to write out
        :return: a single csv file
        """
        with open(single_pdb) as f:
            f = f.readlines()
            temp_glycan_formula = f[1].split('\n')[0]

            temp_f = single_pdb.split('/')[-1]
            if temp_f in self.pdb_missing_formula:
                f = f[1:-1]
            else:
                f = f[2:-1]
            temp_list = [self.convert_singe_pdb_line(i) for i in f]
            temp_pdb_DataFrame = pd.DataFrame(temp_list)
            temp_pdb_DataFrame.columns = ['Atom', 'Atom_Num', 'Atom_Type', 'Monosaccharide_belong',
                                          'residual', 'x', 'y', 'z']
            out_directory = out_directory.replace(' ', '')
            temp_pdb_DataFrame.to_csv(out_directory, index=False)

    @staticmethod
    def read_single_label_csv(single_label, out_directory):
        temp_csv = pd.read_csv(single_label, header=None)
        temp_csv_header = temp_csv.loc[2, :].values
        temp_csv_header[0] = 0.0
        temp_csv = temp_csv.loc[3:, ]
        temp_csv.index = range(len(temp_csv))
        temp_csv.dropna(axis=0, how='all', inplace=True)
        temp_csv = temp_csv.dropna(subset=[0])
        temp_csv.columns = temp_csv_header
        assert len(temp_csv) % 2 == 0
        out_directory = out_directory.replace(' ', '')
        temp_csv.to_csv(out_directory, index= False)

    def read_all_pdb_labels_to_csv(self):
        files = os.listdir(self.pdb_dir_list)
        dir_name = [f for f in files if '-2022' in f]
        print('----------------------------reformulating pdb and label files----------------------------')
        print('Writing new pdb files in csv to:', self.pdb_dir_out_list)
        print('Writing new label files in csv to:', self.shift_labels_dir_out_list)
        for path_pdb in tqdm(dir_name):
            files = os.listdir(path_pdb)
            files_pdb = [f for f in files if '.pdb' in f]
            # in case of .~lock. files in
            files_pdb = [i for i in files_pdb if '.~lock.' not in i]
            for i in range(len(files_pdb)):
                """
                reformulate pdb files
                """
                temp_in_pdb_dir = os.path.join(self.pdb_dir_list, path_pdb, files_pdb[i])
                temp_out_pdb_csv_dir = os.path.join(self.pdb_dir_out_list, files_pdb[i]) + '.csv'
                self.read_single_pdb(temp_in_pdb_dir, temp_out_pdb_csv_dir)

                """
                reformulate label files
                # some issues with the original data
                # Naming problem
                # 7-6-2022/DGalp(3S)b1-4(LFucpa1-3)DGlcp(6S)NAcb1-OME .pdb extra space
        
                # Duplicate glycans 
                # DManpa1-3DManpa1-6(DGalpb1-4DGlcpNAcb1-2DManpa1-3)DManpb1-4DGlcpNAcb1-4DGlcpNAcb1-OH.csv
                # 7-14-2022
                # DManpa1-3DManpa1-6(DGalpb1-4DGlcpNAcb1-2DManpa1-3)DManpb1-4DGlcpNAcb1-4DGlcpNAcb1-OH.xlsx
                # 7-21-2022
                """
                temp_csv_name = files_pdb[i].replace('.pdb', '.csv')
                temp_csv_name = temp_csv_name.replace(" ", "")
                temp_csv_in_dir = os.path.join(path_pdb, temp_csv_name)
                temp_csv_out_dir = self.shift_labels_dir_out_list + temp_csv_name
                self.read_single_label_csv(temp_csv_in_dir, temp_csv_out_dir)


def main():
    R = Reformulate_pdb_csv()
    R.read_all_pdb_labels_to_csv()


if __name__ == "__main__":
    main()
