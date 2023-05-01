# start with the Prefect base image (which itself is using the Pythom slim image) 
#   with tag 2.7.7 to keep versions consistent
FROM prefecthq/prefect:2.7.7-python3.9

COPY docker-requirements.txt .

RUN pip install -r docker-requirements.txt --trusted-host pypi.python.org --no-cache-dir

# Put in our flow code into our Docker image (make sure cwd is the week2/docker/ dir)
# Copy over the data as well
COPY ./ /opt/prefect/flows
COPY ./ /opt/prefect/data
# OR run this:
# RUN mkdir -p /opt/prefect/data/yellow