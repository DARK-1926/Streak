# Campus Dumpster Monitor

A minimal Flask web‑app that demonstrates how a lightweight AI model can be used to detect hazardous waste in images of a library dumpster.

## Quick start
```bash
git clone <repo-url>
cd campus_dumpster_monitor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_tests.py   # runs the test suite
python scripts/run_demo.py   # starts the dev server at http://127.0.0.1:5000
```

Upload an image on the home page – the backend returns the top‑3 predicted waste categories.

## Project layout
(see the folder tree in the specification). The core AI lives in `detector/`; the Flask UI lives in `app/`.

## Testing
```bash
python run_tests.py
```
The single script imports `pytest` and exits with the appropriate status code.
