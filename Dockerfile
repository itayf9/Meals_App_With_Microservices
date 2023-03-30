FROM python:3.9
WORKDIR ./app
COPY . .
RUN pip install flask
RUN pip install requests
EXPOSE 8000

CMD ["python3", "main.py"]