# base image to run from/use -- base it on Python 3.9
FROM python:3.9 

# command to run
RUN pip install pandas

# specify the working directory of where in the image we work with the file below
WORKDIR /app

# copy pipeline file from current working directory to docker image
COPY pipeline.py pipeline.py

# override the entry point
ENTRYPOINT [ "bash" ]

# build the image with `docker build -t test:pandas .` --> test = img name, pandas = tag
# run the image with `winpty docker run -it test:pandas`
# kill python with Ctrl+C
# Kill Docker image with Ctrl+D