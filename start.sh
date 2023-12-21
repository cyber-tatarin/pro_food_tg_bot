#!/bin/bash
python -m root.tg.main & uvicorn root.web.main:app --host 0.0.0.0 --port $PORT
