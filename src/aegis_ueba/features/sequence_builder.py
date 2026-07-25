from __future__ import annotations

import numpy as np


def build_sequences(matrix: np.ndarray, entity_ids: list[str], sequence_length: int) -> tuple[np.ndarray, np.ndarray]:
    sequences = []
    indices = []
    start = 0
    n_rows = matrix.shape[0]
    while start < len(entity_ids):
        current = entity_ids[start]
        end = start
        while end < len(entity_ids) and entity_ids[end] == current:
            end += 1
        block = matrix[start:end]
        if hasattr(block, "toarray"):
            block = block.toarray()
        else:
            block = np.asarray(block)
        for i in range(sequence_length, block.shape[0] + 1):
            sequences.append(block[i - sequence_length : i])
            indices.append(start + i - 1)
        start = end
    if not sequences:
        return np.empty((0, sequence_length, matrix.shape[1])), np.empty((0,), dtype=int)
    return np.stack(sequences), np.array(indices)
