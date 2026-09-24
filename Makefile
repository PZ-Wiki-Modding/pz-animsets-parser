.ONESHELL:
.PHONY: help run

SHELL := /bin/bash

help:
	@echo "PZ AnimSets Parser"
	@echo "Available targets:"
	@echo "  run:   Run the parser"

run:
	@echo "Parse all"
	./.venv/bin/python ./scripts/parse_AnimNode.py
