FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install --with-deps

EXPOSE ${PORT:-8501}

CMD streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}