from prefect.infrastructure.docker import DockerContainer

# Alternative to creating a Docker Container block in the Orion UI
docker_block = DockerContainer(
    # insert your image here with you Dockerhub username
    image='[Dockerhub username]/prefect:zoom',
    image_pull_policy='ALWAYS',
    auto_remove=True,
)

docker_block.save('zoom', overwrite=True)
