FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ln -s ../jetsoftime jetsoftime && \
    ln -s ../jetsoftime/sourcefiles/names.txt names.txt && \
    ln -s ../jetsoftime/sourcefiles/patch.ips patch.ips && \
    ln -s ../jetsoftime/sourcefiles/flux flux && \
    ln -s ../jetsoftime/sourcefiles/patches patches && \
    ln -s ../jetsoftime/sourcefiles/pickles pickles

RUN python manage.py migrate

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
