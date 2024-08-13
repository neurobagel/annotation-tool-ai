#!/bin/bash
python3 app/api.py --host 0.0.0.0 --port 9000 &
ollama serve &&
ollama pull gemma &&
ollama run gemma 





