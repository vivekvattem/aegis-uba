from __future__ import annotations

from collections import defaultdict


class SequenceState:
    def __init__(self, sequence_length: int) -> None:
        self.sequence_length = sequence_length
        self.buffers: dict[str, list[list[float]]] = defaultdict(list)

    def append(self, entity_id: str, vector: list[float]) -> None:
        buffer = self.buffers[entity_id]
        buffer.append(vector)
        if len(buffer) > self.sequence_length:
            buffer.pop(0)

    def ready(self, entity_id: str) -> bool:
        return len(self.buffers[entity_id]) >= self.sequence_length

    def get(self, entity_id: str) -> list[list[float]]:
        return self.buffers[entity_id][-self.sequence_length :]
