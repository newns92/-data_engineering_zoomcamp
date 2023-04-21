# base image to run from/use -- base it on Python 3.9
FROM python:3.9 

# command to run
RUN pip install pandas

# override the entry point
ENTRYPOINT [ "bash" ]