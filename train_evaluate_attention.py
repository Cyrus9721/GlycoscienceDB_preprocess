import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import dgl
import dgl.nn as dglnn
from dgl import AddSelfLoop
from model_zoo.NMR_gcn import NMR_GCN
from create_graph_data import create_graph
from tqdm import tqdm


class NMR_prediction:
    def __init__(self, results_dir='results/results_all_carbon.csv',
                 model_dir='model_state/Model_no_residual_embed_Carbon_best_only_node_embedding.pt', num_epoch=1000, lr=1e-2, weight_decay=5e-4):
        self.results_dir = results_dir
        self.model_dir = model_dir
        self.num_epoch = num_epoch
        self.lr = lr
        self.weight_decay = weight_decay

    def evaluate(self, g, features1, features2, features3, features4, features5, shift_values, mask, model, print_out=False):
        model.eval()
        with torch.no_grad():
            predict_shift = model(g, features1, features2, features3, features4, features5)
            predict_shift_test = predict_shift[mask]
            actual_shift_test = shift_values[mask]

            correct = torch.sum((predict_shift_test - actual_shift_test) ** 2)

            if print_out:
                df_temp = pd.DataFrame([predict_shift_test.cpu().numpy(), actual_shift_test.cpu().numpy()]).T
                df_temp.to_csv(self.results_dir, index=False)
            print(len(predict_shift_test))
            return np.sqrt(correct.item() * 1.0 / len(predict_shift_test))

    def train(self, g, features1, features2, features3, features4, features5, shift_values, masks, model):
        # define train/val samples, loss function and optimizer
        train_mask = masks[0]
        test_mask = masks[1]
        loss_fcn = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        best_loss = 1000
        # training loop
        for epoch in tqdm(range(self.num_epoch)):
            model.train()
            logits = model(g, features1, features2, features3, features4, features5)

            loss = loss_fcn(logits[train_mask], shift_values[train_mask])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            mse_test = self.evaluate(g, features1, features2, features3, features4, features5, shift_values, test_mask, model)
            mse_train = self.evaluate(g, features1, features2, features3, features4, features5, shift_values, train_mask, model)
            print(
                "Epoch {:05d} | Loss {:.4f} | train_RMSE {:.4f} | test_RMSE {:.4f} ".format(
                    epoch, loss.item(), mse_train, mse_test
                )
            )

            if loss.item() < best_loss:
                best_loss = loss.item()
                torch.save(model.state_dict(), self.model_dir)
        print('best loss:', best_loss)


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    C = create_graph()
    g, test_index = C.create_all_graph()

    pd.DataFrame(test_index).to_csv('data/test_index.csv', index=False)

    g = g.int()
    g = g.to(device)
    features = g.ndata["feat"]
    labels = g.ndata["shift_value"]
    # masks = g.ndata['train_mask'], g.ndata['test_mask']
    # masks = g.ndata['train_hydrogen_mask'], g.ndata['test_hydrogen_mask']
    masks = g.ndata['train_carbon_mask'], g.ndata['test_carbon_mask']
    print(features.dtype)
    print(labels.dtype)
    # model = NMR_GCN(in_size=576, hid_size=[256, 128, 64, 32], out_size=1).to(device)
    model = NMR_GCN(in_size=512, hid_size=[256, 128, 64, 32], out_size=1).to(device)
    # model training

    NMR_prediction = NMR_prediction()
    print("Training...")
    NMR_prediction.train(g, features, labels, masks, model)

    # test the model
    print("Testing...")
    saved_model = NMR_GCN(in_size=512, hid_size=[256, 128, 64, 32], out_size=1).to(device)
    saved_model.load_state_dict(torch.load(NMR_prediction.model_dir))
    acc = NMR_prediction.evaluate(g, features, labels, masks[1], saved_model)
    print("MSE {:.4f}".format(acc))
