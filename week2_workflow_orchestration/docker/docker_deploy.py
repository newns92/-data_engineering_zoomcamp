from prefect.infrastructure.docker import DockerContainer
from prefect.deployments import Deployment
# Import our parent flow function from our ETL Python file
from parameterized_flow import etl_parent_flow

# Connect to the Docker Container block we've built
docker_block = DockerContainer.load('zoom')

# Create a deployment instance from a Python file rather than the CLI
docker_deployment = Deployment.build_from_flow(
    flow=etl_parent_flow,  # specify the flow to import the function from
    name='docker-flow',  # Name the deployment
    infrastructure=docker_block,
)

# The above code builds the deployment, now actually tell the Prefect API server
#   that we have one and "apply" it
if __name__ == '__main__':
    docker_deployment.apply()
    print("Docker deployment created")
