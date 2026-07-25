PYTHON ?= python
CONFIG ?= configs/fast.yaml

.PHONY: generate train evaluate pipeline replay test

generate:
	$(PYTHON) scripts/generate_data.py --config $(CONFIG)

train:
	$(PYTHON) scripts/train.py --config $(CONFIG)

evaluate:
	$(PYTHON) scripts/evaluate.py --config $(CONFIG)

pipeline:
	$(PYTHON) scripts/run_pipeline.py --config $(CONFIG)

replay:
	$(PYTHON) scripts/replay_stream.py --config $(CONFIG)

test:
	pytest -q
