install:
\tpython -m pip install -r requirements.txt

test:
\tpython -m pytest -q

run:
\tpython -m src.cli --question "teste local"
