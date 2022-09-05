FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1

#
#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV APP_DIR=/app/
WORKDIR $APP_DIR

# Install dependencies:
COPY ./requirements.txt $APP_DIR
RUN pip install -r requirements.txt

COPY . $APP_DIR
#RUN /bin/bash -c "echo list dir..."
#RUN /bin/bash -c "ls -la $APP_DIR"

#EXPOSE 8000
# Run the application:
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]