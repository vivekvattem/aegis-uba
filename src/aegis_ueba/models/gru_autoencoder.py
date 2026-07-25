from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class _GruAutoencoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, dropout: float) -> None:
        super().__init__()
        self.encoder = nn.GRU(input_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.decoder = nn.GRU(hidden_dim, hidden_dim, num_layers=num_layers, batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.output = nn.Linear(hidden_dim, input_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _, hidden = self.encoder(x)
        repeated = hidden[-1].unsqueeze(1).repeat(1, x.size(1), 1)
        decoded, _ = self.decoder(repeated)
        return self.output(decoded)


@dataclass
class GruTrainingResult:
    train_loss: float
    val_loss: float


class GruSequenceAutoencoder:
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int, dropout: float, lr: float, epochs: int, batch_size: int, patience: int) -> None:
        self.device = torch.device("cpu")
        self.model = _GruAutoencoder(input_dim, hidden_dim, num_layers, dropout).to(self.device)
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.patience = patience

    def fit(self, train_sequences: np.ndarray, val_sequences: np.ndarray) -> GruTrainingResult:
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        loss_fn = nn.MSELoss()
        train_loader = DataLoader(TensorDataset(torch.tensor(train_sequences, dtype=torch.float32)), batch_size=self.batch_size, shuffle=True)
        val_tensor = torch.tensor(val_sequences, dtype=torch.float32, device=self.device)
        best_loss = float("inf")
        best_state = None
        patience_left = self.patience
        final_train = float("inf")
        final_val = float("inf")
        for _ in range(self.epochs):
            self.model.train()
            losses = []
            for (batch,) in train_loader:
                batch = batch.to(self.device)
                optimizer.zero_grad()
                recon = self.model(batch)
                loss = loss_fn(recon, batch)
                loss.backward()
                optimizer.step()
                losses.append(float(loss.item()))
            final_train = float(np.mean(losses)) if losses else float("inf")
            self.model.eval()
            with torch.no_grad():
                val_recon = self.model(val_tensor)
                final_val = float(loss_fn(val_recon, val_tensor).item())
            if final_val < best_loss:
                best_loss = final_val
                best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                patience_left = self.patience
            else:
                patience_left -= 1
                if patience_left <= 0:
                    break
        if best_state is not None:
            self.model.load_state_dict(best_state)
        return GruTrainingResult(train_loss=final_train, val_loss=final_val)

    def score(self, sequences: np.ndarray) -> np.ndarray:
        self.model.eval()
        tensor = torch.tensor(sequences, dtype=torch.float32, device=self.device)
        with torch.no_grad():
            recon = self.model(tensor)
        errors = torch.mean((recon - tensor) ** 2, dim=(1, 2)).cpu().numpy()
        if len(errors) == 0:
            return errors
        return (errors - errors.min()) / max(1e-9, errors.max() - errors.min())
