#!/bin/sh

coverage run --branch --omit 'venv/*' -m unittest discover
coverage report
coverage annotate
