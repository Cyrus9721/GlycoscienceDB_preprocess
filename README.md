## Data cleaning and preprocessing directory for CASPER and Glycoscience.DB

### Data preprocessing doc for Glycoscience.

+ Comments from domain experts in first inspection [comments1](preprocess_manual/linear_check_email_1.pdf), [comments2](preprocess_manual/linear_check_email_2.pdf).

+ Manual annotation from domain experts in second inspection [annotation1](preprocess_manual/nonlinear_preprocess_doc_revised.pdf), [annotation2](preprocess_manual/nonlinear_preprocess_doc_revised.pdf).

The data cleaning and preprocessing pipeline can be divided into several parts:

1, Reformulate all the .pdb file and label file into interpretable format. 

2, A general data cleaning apply to both linear glycans and branched glycans, unifying and correcting the atom-level and monosaccharide format from various labs

3, For linear glycans, the major error is from the shift of monosaccharide IDs from .pdb file and label file. Some data refer non-monosaccharide components as monosaccharide components. We solve this error by manually inspecting all the linear glycans.

4, For non-linear glycans, the major error is from the inconsistent match between monosaccharide IDs from .pdb file and label file. We solve this error by manually inspecting all the non-linear glycans. 

5, We apply an outlier check between the groud truth NMR shift and the predicted NMR shift on the baseline GNN model, to see whether the outlier is come from the omissions in step 2, 3, 4. If yes, we then go back to previous steps and correct our mistakes. 
### Example run on CASPER data.  

Preprocess the PDB files and their labels(in order): <br />
```
python reformulate_PDB_labels.py
python align_PDB_labels.py
python create_adjaency_matrix_from_labeled_pdb.py
```
Generate node embeddings: 
```
python node_embeddings.py
```
Train the gcn model for combined prediction of Carbon and Hydrogen: 
```
python train_evaluate.py
```
<br />
Predicting atom shift in glycans from nmr data <br />
The model is trainined on 391 glycans and tested on 40 glycans. <br />
Current RMSE for Carbon: 1.61<br />
Current RMSE for Carbon without node embedding: 1.84<br />
Current RMSE for Hydrogen: 0.10<br />
Current RMSE for Hydrogen without node embedding: 0.19<br />

![gcn_all](/figures/gcn_all.png?raw=true) <br />

Next step: <br />
1, train separate gnn for Carbon and Hydrogen (Done).<br />
2, change model architecture. <br />
3, use prior knowledge based node embeddings.<br />
4, use prior knowledge based edge embeddings.<br />

