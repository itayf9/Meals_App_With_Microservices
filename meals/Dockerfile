FROM python:3.9
WORKDIR ./app
COPY . .
RUN pip install flask
RUN pip install requests
RUN pip install pymongo
EXPOSE 5001

CMD ["python3", "meals_main.py"]