FROM python:3.13

COPY jjjquery.mo.py jjjquery.mo.py
RUN pip install marimo abc-radio-wrapper typing-extensions --no-cache-dir

ENTRYPOINT ["marimo", "run", "jjjquery.mo.py", "--host", "0.0.0.0", "--port", "80", "--headless"]
