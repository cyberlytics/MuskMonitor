FROM python:3.11-slim
ENV FLASK_APP=webserver.py
WORKDIR /app
COPY . .
RUN apt-get update \
    && apt-get upgrade -y \
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && python3 -m pip install pytest
EXPOSE 5000
CMD /bin/bash -c "python3 tesla_stock/save_in_db.py && flask run --host=0.0.0.0"
# CMD /bin/bash -c "flask run --host=0.0.0.0"