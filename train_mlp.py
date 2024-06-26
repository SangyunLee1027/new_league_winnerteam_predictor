import pandas as pd
import ast
from Model.data_process import MLPDataset_For_League
from torch.utils.data import DataLoader
from Model.BERT import BERT,BERTLM
from Model.WinnerPredictModel import Winner_Predictor, Winner_Predictor_Trainer
import torch

if __name__ == '__main__':
    df = pd.read_csv("Data/match_data_2.csv")
    df["teams"] = df["teams"].apply(lambda x : ast.literal_eval(x))


    champ_idx = {}
    with open("Model/champ_idx.txt", 'r') as file:
        for line in file:
            pair = ast.literal_eval(line)
            champ_idx.update({pair[0]: pair[1]})



    for i in range(len(df["teams"])):
        for j in range(len(df["teams"][i])):
            df["teams"][i][j] = champ_idx[df["teams"][i][j]]


    train_datas = [[df["teams"][i][:5], df["teams"][i][5:], df["winner"][i]] for i in range(len(df))]


    MAX_LEN = 13
    vocab_size = 2000

    train_data = MLPDataset_For_League(
    train_datas, seq_len=MAX_LEN)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    train_loader = DataLoader(
    train_data, batch_size=16, shuffle=True, pin_memory=True)

    bert_model = BERT(
    vocab_size=vocab_size,
    d_model= 32,
    n_layers=8,
    heads=8,
    dropout=0.1,
    device = device
    )

    bert_ = BERTLM(bert_model, vocab_size)
    bert_.load_state_dict(torch.load("Trained_Model/bert_model_final"))


    wpm = Winner_Predictor(bert_).to(device)
    wpm_trainer = Winner_Predictor_Trainer(wpm, train_loader, lr= 0.001, device='cuda')


    prev_epochs = 0
    epochs = 20
    for epoch in range(prev_epochs, epochs):
        wpm_trainer.train(epoch)

        torch.save(wpm.state_dict(), "Trained_Model/mlp_model")
    