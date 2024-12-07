FROM python:3.13

COPY marimo.py marimo.py
RUN pip install marimo --no-cache-dir

ENTRYPOINT ["marimo", "run", "marimo.py", "--host", "0.0.0.0", "--port", "80", "--headless"]
