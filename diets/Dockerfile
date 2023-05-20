FROM python:3.9
WORKDIR ./app
COPY . .
RUN pip install flask==2.2.3
RUN pip install requests
RUN pip install pymongo
EXPOSE 5002

CMD ["python3", "diets_main.py"]