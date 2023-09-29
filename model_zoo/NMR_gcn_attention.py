import torch
import torch.nn as nn
import torch.nn.functional as F
import dgl
import dgl.nn as dglnn
from dgl.nn.pytorch import GraphConv
from dgl import AddSelfLoop


class NMR_GCN(nn.Module):
    def __init__(self, in_size1, in_size2, in_size3, in_size4, in_size5, hid_size, out_size):
        super().__init__()
        self.layers = nn.ModuleList()

        self.front_dense1 = nn.Linear(in_size1, hid_size[0])

        self.front_dense2 = nn.Linear(in_size2, hid_size[0])

        self.front_dense3 = nn.Linear(in_size3, hid_size[0])

        self.front_dense4 = nn.Linear(in_size4, hid_size[0])

        self.front_dense5 = nn.Linear(in_size5, hid_size[0])

        self.w1 = torch.nn.Parameter(torch.randn(1))
        self.w2 = torch.nn.Parameter(torch.randn(1))
        self.w3 = torch.nn.Parameter(torch.randn(1))
        self.w4 = torch.nn.Parameter(torch.randn(1))
        self.w5 = torch.nn.Parameter(torch.randn(1))



        # two-layer GCN
        self.layers.append(
            GraphConv(hid_size[0], hid_size[1], activation=F.relu)
        )
        self.layers.append(GraphConv(hid_size[1], hid_size[2]))
        self.dropout = nn.Dropout(0.5)
        self.back_dense1 = nn.Linear(hid_size[2], hid_size[3])
        self.back_dense2 = nn.Linear(hid_size[3], out_size)

    def forward(self, g, features1, features2, features3, features4, features5):
        h1 = features1
        h1 = self.front_dense1(h1)

        h2 = features2
        h2 = self.front_dense2(h2)

        h3 = features3
        h3 = self.front_dense3(h3)

        h4 = features4
        h4 = self.front_dense4(h4)

        h5 = features5
        h5 = self.front_dense5(h5)

        h = h1 * self.w1 + h2 * self.w2 + h3 * self.w3 + h4 * self.w4 + h5 * self.w5

        for i, layer in enumerate(self.layers):
            if i != 0:
                h = self.dropout(h)
            h = layer(g, h)
        h = self.back_dense1(h)
        h = self.back_dense2(h)
        h = h.view(-1)
        return h
