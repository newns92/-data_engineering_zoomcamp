# base image to run from/use
FROM python:3.9

# command to run
RUN pip install pandas

# specify the working directory of where in the Image we work with the file below
WORKDIR /app

# copy pipeline file from current working directory to docker image
COPY pipeline.py pipeline.py

# override the entry point
# ENTRYPOINT [ "bash" ]
ENTRYPOINT [ "python", "pipeline.py" ]