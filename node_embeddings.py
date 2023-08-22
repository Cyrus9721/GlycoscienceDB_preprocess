# @Author  : Zizhang Chen
# @Contact : zizhang2@outlook.com
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import torch
import torch.nn as nn


class create_node_embeddings:
    """
    generate embeddings for atom type, residual belongs and monosaccharide number
    """

    def __init__(self, data_dir='data/directory_reformulate_combined/', out_atom_embed='graph/atom_embed.csv',
                 out_residual_embed='graph/residual_embed.csv', out_monosaccharide_embed='graph/monosaccharide_embed.csv', seed=97211):
        self.data_dir = data_dir
        self.out_atom_embed = out_atom_embed
        self.out_residual_embed = out_residual_embed
        self.out_monosaccharide_embed = out_monosaccharide_embed
        self.seed = seed

    def create_all_embeddings(self, atom_dim=64, residual_dim=32, mono_dim=32):
        """
        :param atom_dim: atom feature dimension
        :param residual_dim: residual feature dimension
        :param mono_dim: monosaccharide feature dimension
        :return: three embedding dataframe: dimension * type
        """
        torch.manual_seed(self.seed)
        files_labels_list = os.listdir(self.data_dir)
        atom_type_list = []
        residual_list = []
        monosaccharide_belong_list = []

        for i in tqdm(range(len(files_labels_list))):
            f1 = files_labels_list[i]
            temp_df = pd.read_csv(os.path.join(self.data_dir, f1))
            atom_type_list.extend(list(temp_df['Atom_Type'].values))
            residual_list.extend(list(temp_df['residual'].values))
            monosaccharide_belong_list.extend(list(temp_df['Monosaccharide_belong'].values))
        """
        get the unique type 
        """
        atom_type_list = np.sort(np.unique(atom_type_list))
        residual_list = np.sort(np.unique(residual_list))
        monosaccharide_belong_list = np.sort(np.unique(monosaccharide_belong_list))

        atom_embedding = nn.Embedding(len(atom_type_list), embedding_dim=atom_dim).weight.clone().detach().numpy()
        df_atom_embedding = pd.DataFrame(atom_embedding.T)
        df_atom_embedding.columns = atom_type_list

        residual_embedding = nn.Embedding(len(residual_list),
                                          embedding_dim=residual_dim).weight.clone().detach().numpy()
        df_residual_embedding = pd.DataFrame(residual_embedding.T)
        df_residual_embedding.columns = residual_list

        monosaccharide_embedding = nn.Embedding(len(monosaccharide_belong_list),
                                                embedding_dim=mono_dim).weight.clone().detach().numpy()
        df_monosaccharide_embedding = pd.DataFrame(monosaccharide_embedding.T)
        df_monosaccharide_embedding.columns = monosaccharide_belong_list

        return df_atom_embedding, df_residual_embedding, df_monosaccharide_embedding


def main():
    C = create_node_embeddings()
    df_atom_embedding, df_residual_embedding, df_monosaccharide_embedding = C.create_all_embeddings(atom_dim=512, residual_dim=64, mono_dim=64)
    df_atom_embedding.to_csv(C.out_atom_embed, index=False)
    df_residual_embedding.to_csv(C.out_residual_embed, index=False)
    df_monosaccharide_embedding.to_csv(C.out_monosaccharide_embed, index=False)


if __name__ == "__main__":
    main()
