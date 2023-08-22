# @Author  : Zizhang Chen
# @Contact : zizhang2@outlook.com
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import torch
import torch.nn as nn
import dgl
import warnings

warnings.filterwarnings("ignore")


class create_graph:
    def __init__(self, data_dir='data/directory_reformulate_combined/', adj_dir='graph/directory_graph_connection/',
                 interaction_dir='graph/directory_graph_interaction/', atom_embed_dir='graph/atom_embed.csv',
                 residual_embed_dir='graph/residual_embed.csv', mono_embed_dir='graph/monosaccharide_embed.csv',
                 num_test=40, seed=97211):
        self.data_dir = data_dir
        self.adj_dir = adj_dir
        self.interaction_dir = interaction_dir
        self.atom_embed_dir = atom_embed_dir
        self.residual_embed_dir = residual_embed_dir
        self.mono_embed_dir = mono_embed_dir
        self.num_test = num_test
        self.seed = seed

        # files used to build a graph
        self.files_labels_list = os.listdir(self.data_dir)
        self.adj_list = os.listdir(self.adj_dir)
        self.interaction_list = os.listdir(self.interaction_dir)

        # embeddings for nodes
        self.atom_embed = pd.read_csv(self.atom_embed_dir)
        self.residual_embed = pd.read_csv(self.residual_embed_dir)
        self.mono_embed = pd.read_csv(self.mono_embed_dir)

    def create_single_graph(self, f1, in_train_set, in_test_set):
        """
        :param f1: name of the glycan files
        :param in_train_set: whether this glycan in training set
        :param in_test_set:  whether this glycan in testing set
        :return: a dgl graph object
        """

        """
        Add different mask for carbon and hydrogen
        """
        carbon_list = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
        hydrogen_list_1_6 = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H61', 'H62']
        """
        Read in labeled pdb files with corresponding adjacency matrix.
        """
        temp_df = pd.read_csv(os.path.join(self.data_dir, f1))
        temp_adj = np.array(pd.read_csv(os.path.join(self.adj_dir, 'edges_' + f1)))

        """
        Create node features, Carbon and Hydrogen masks, training masks, testing masks.
        """
        # embedding_matrix = torch.zeros([len(temp_df), len(self.atom_embed) + len(self.residual_embed) + len(self.mono_embed)], dtype=torch.float32)
        # embedding_matrix = torch.zeros([len(temp_df), len(self.atom_embed) + len(self.mono_embed)], dtype=torch.float32)
        embedding_matrix = torch.zeros([len(temp_df), len(self.atom_embed)], dtype=torch.float32)

        carbon_mask = torch.zeros(len(temp_df), dtype=torch.bool)
        hydrogen_mask = torch.zeros(len(temp_df), dtype=torch.bool)

        temp_atom_list = temp_df['Atom_Type'].values
        temp_residual_list = temp_df['residual'].values.astype(str)
        temp_mono_list = temp_df['Monosaccharide_belong'].values
        temp_label_list = temp_df['labels'].values
        for i in range(len(temp_df)):
            c_atom = temp_atom_list[i]
            c_redisual = temp_residual_list[i]
            c_mono = temp_mono_list[i]

            # embedding_matrix[i, :] = torch.tensor(np.concatenate([self.atom_embed[c_atom],
            #                                                       self.residual_embed[c_redisual],
            #                                                       self.mono_embed[c_mono]], axis=0))

            # embedding_matrix[i, :] = torch.tensor(np.concatenate([self.atom_embed[c_atom], self.mono_embed[c_mono]], axis=0))
            embedding_matrix[i, :] = torch.tensor(self.atom_embed[c_atom].values)

            if (c_atom in carbon_list) and (temp_label_list[i] != -1):
                carbon_mask[i] = True
            if c_atom in hydrogen_list_1_6:
                hydrogen_mask[i] = True

        label = torch.tensor(temp_df['labels'].values, dtype=torch.float32)
        Carbon_Hydrogen_mask = torch.tensor(temp_df['labels'].values != -1.0, dtype=torch.bool)

        if in_train_set and (not in_test_set):
            train_mask = Carbon_Hydrogen_mask.clone()
            test_mask = torch.zeros(len(label), dtype=torch.bool)

            train_carbon_mask = carbon_mask
            test_carbon_mask = torch.zeros(len(label), dtype=torch.bool)

            train_hydrogen_mask = hydrogen_mask
            test_hydrogen_mask = torch.zeros(len(label), dtype=torch.bool)


        elif (not in_train_set) and in_test_set:
            train_mask = torch.zeros(len(label), dtype=torch.bool)
            test_mask = Carbon_Hydrogen_mask.clone()

            train_carbon_mask = torch.zeros(len(label), dtype=torch.bool)
            test_carbon_mask = carbon_mask

            train_hydrogen_mask = torch.zeros(len(label), dtype=torch.bool)
            test_hydrogen_mask = hydrogen_mask


        else:
            raise Exception("This graph should either in training set or testing set")

        """
        Create graph with node data from adjacency matrix
        """
        src, dst = np.nonzero(temp_adj)
        g = dgl.graph((src, dst))
        g.ndata['feat'] = embedding_matrix
        g.ndata['shift_value'] = label
        g.ndata['Carbon_Hydrogen_mask'] = Carbon_Hydrogen_mask
        g.ndata['train_mask'] = train_mask
        g.ndata['test_mask'] = test_mask

        g.ndata['train_carbon_mask'] = train_carbon_mask
        g.ndata['test_carbon_mask'] = test_carbon_mask
        g.ndata['train_hydrogen_mask'] = train_hydrogen_mask
        g.ndata['test_hydrogen_mask'] = test_hydrogen_mask

        # g.ndata['atom_type'] = temp_atom_list
        return g

    def generate_train_test_split(self):
        np.random.seed(self.seed)
        total_g = len(self.files_labels_list)
        train_test_indicator = np.zeros(total_g)

        # randomly choose index of test files
        test_index = np.sort(np.random.choice(range(total_g), size=self.num_test, replace=False))
        train_test_indicator[test_index] = 1
        return train_test_indicator

    def create_all_graph(self):
        g = dgl.DGLGraph()
        # g = dgl.graph()
        train_test_indicator = self.generate_train_test_split()
        print('--------------------------loading NMR Graph-------------------------------')
        for i in tqdm(range(len(self.files_labels_list))):
            f = self.files_labels_list[i]
            if train_test_indicator[i]:
                temp_g = self.create_single_graph(f, in_train_set=False, in_test_set=True)
            else:
                temp_g = self.create_single_graph(f, in_train_set=True, in_test_set=False)

            g = dgl.batch([g, temp_g])

        return g, train_test_indicator


def main():
    C = create_graph()
    large_graph = C.create_all_graph()
    print(large_graph)


if __name__ == "__main__":
    main()
