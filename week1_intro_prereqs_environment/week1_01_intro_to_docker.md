# Introduction to Docker


## Installation
- Just follow the instructions on the download page, like the one for Windows OS here: https://docs.docker.com/desktop/install/windows-install/
    - Test this by running Docker Desktop (and sign in if need be), and in a terminal window (say, Git bash), load and run the `hello-world` Docker image via `docker run hello-world`        
    - Can then further test with `docker run -it ubuntu bash`, where `-it` means interactive mode (so we can type), and `bash` is a command to run in the `ubuntu` image being ran (then exit via `exit`)
        - *NOTE*: In Git bash, may need to preface with `winpty`, such as like `winpty docker run -it ubuntu bash`
    - Can also run specific versions of Python, say Python 3.9, via `winpty docker run -it python:3.9`
        - Can overide the entry point (i.e., what is executed when we run a container) of the image via the `entrypoint=` argument, such as via the command `winpty docker run -it --entrypoint=bash python:3.9`


## What is Docker?
- ***Docker*** is an OS-level **virtualization** to deliver software in packages called ***containers*** (i.e., sandboxed processes running on a host machine that bundle their *own* software, libraries, and configuration files, and are **isolated** from all other processes running on their host)
    - Example: A container with an Ubuntu OS, Python 3.9 with pandas, and a Postgres connection library in order to run a data ingestion pipeline
        - Also with separate containers containing a Postgres database to store ingestion results and another containing pgAdmin (a standard web-based GUI for Postgres data exploration and querying)
    - Could run these containers both locally or on a cloud service like Google Cloud Platform (GCP)
- A ***container***:
    - Is a *runnable* **instance** of an ***image***
    - Can be created, started, stopped, moved, or deleted using the Docker API or the CLI
    - Can be run on local machines, virtual machines (VMs), or deployed to the cloud
    - Is portable (and can be run on *any* OS)
    - Is isolated from other containers and runs its *own* software, binaries, configurations, etc.
- An ***image***:
    - Is a *running* container that uses an *isolated* filesystem
    - This isolated filesystem is provided by an image, and the image *must* contain everything needed to run an application (all dependencies, configurations, scripts, binaries, etc.) 
    - The image also contains *other* configurations for the container, such as environment variables, a default command to run, and other metadata
- *What's the difference?*
    - Docker images and containers are both application deployment technologies
    - Docker **images** are *read-only* templates that **contain instructions for creating a container**
        - A Docker image is a *snapshot* or *blueprint* of the libraries and dependencies required inside a container for an application to run
    - A Docker **container** is a self-contained, runnable software application or service
    - A Docker **image** is the *template* loaded *onto* the container to run it, like a set of instructions
        - *A Docker image executes code in a Docker container*, and an *instance* of an image is a container        
    - You store images for sharing and reuse, but you create and destroy containers over an application's lifecycle
    - **You can have many running containers of the same image**
- We use Docker for **reproducibility**, **local experiments**, **integration tests (CI/CD, general best software engineering (SWE) practices, etc.)**, **running pipelines on the cloud (AWS Batch, Kubernets (K8's) jobs, etc.)**, **Spark**, **server-less work (AWS Lambda, Google functions, etc.)**


## Dockerfile
- To build an image, you'll need to use a **Dockerfile**, a text-based file with no file extension that *contains a script of instructions* that Docker uses to build a container **image** (rememberm, an image is a *running* container that uses an *isolated* filesystem)
    - Dockerfiles *specify what goes into your image* (what's the base, what other modules need to be added and/or copied, commands that need to be run, etc.)
    - For example:
        ```yml
        # Base image to run from/use
        FROM python:3.9

        # Command to run
        RUN pip install pandas

        # Override the entry point
        ENTRYPOINT [ "bash" ]
        ```
- The `docker build -t <image-name> .` CLI command uses the Dockerfile to *build* a new image using the Dockerfile in the *current* directory (via the `.` at the end of the command), while also **tagging** the image with a human-readable image name
    - For example, `winpty docker build -t test:pandas .`
    - *Must **rebuild** images after any changes are made*
- You can then run a container using the `docker run` CLI command while specifying the name of an image
    - Can run `winpty docker run -it test:pandas` without that `--entrypoint=bash` parameter in the CLI command
    - Can use the `-d` flag (short for `--detach`) to run a container in the background (Docker starts your container and returns you to the terminal prompt)
- `docker ps` will show all running containers
- To remove a container, you first need to *stop* it
    - Run `docker stop <container-id>` after getting the container ID from `docker ps`, then run  `docker rm <container-id>`

### Persisting the Docker Database
- When a container runs, it uses the various **layers** from an image for its filesystem
- Each container also gets its own "scratch space" to create/update/remove files
- *Any changes won't be seen in another container, even if they're using the same image*
- Each container starts from the image definition *each time it starts*
- While containers can create, update, and delete files, those changes are lost when you remove the container and Docker isolates all changes to that container
- With ***Volumes***, you can change all of this, as they **provide the ability to connect *specific* filesystem paths of the container *back to the host machine***
- There are *2 main types of volumes*:
    1. A **volume mount**
        - If you **mount** a directory in the container, changes in that directory are also seen on the host machine
        - If you mount that same directory across container restarts, you'd see the same files
        - If you can **persist** a file on the host and make it available to the next container, it should be able to pick up where the last one left off
            - By creating a volume and attaching (often called "mounting") it to the directory where you stored the data, you can persist the data
    2. A **bind mount**
        - Lets you share a directory from the host's filesystem into the container
        - When working on an application, you can use a bind mount to mount source code into the container
        - The container sees the changes you make to the code *immediately*, as soon as you save a file, which means you can run processes in the container that watch for filesystem changes and respond to them
        - Using bind mounts is common for local DEV setups
            - The advantage is that the DEV machine doesn't need to have all of the build tools and environments installed, since with a single `docker run` command, Docker pulls dependencies and tools

### Multi-container Applications
- Separate containers let you version and update versions in isolation
- Might have to scale different applications differently (APIs and front-ends vs. databases, for example)
- Containers, by default, run in *isolation* and don't know anything about other processes or containers on the same machine
- To allow one container to talk to another, use ***networking***
    - *If you place the 2 containers on the same **network**, they can talk to each other*


## Docker Compose
- With ***Docker Compose***, you can share your application stacks in a much easier way and let others spin them up with a single, simple command
    - It is a tool that helps you **define and share multi-container applications**
- With **Compose**, you can create a YML file to define the services and, with a single command, can spin everything up (or tear it all down)
    - Docker Compose is used to encode all things that would normally have to be added as flags when running a `docker run` command which typically make them really long
    - To avoid having to create long `docker run` commands, all instructions can be put instead into a `docker-compose.yml` file and ran with a simple `docker compose up` command
        - Usually, a project would have a `Dockerfile` that specifies how to build an image, and that Dockerfile will be linked to the `docker-compose.yml` file
- The big advantage of using Compose = you can define your application stack in a file, keep it at the root of your project repo (it's now version controlled), and easily enable someone else to contribute to your project (via cloning the repo, for example)
- Unlike Dockerfiles, which give instructions on how to build a *particular* image, **Docker Compose is an orchestration tool that allows you to spin up *multiple* containers with 1 command and specify their relationships to one another** 
    - It also comes with some free perks, like the creation of a common network for all of the containers specified in the `.yml` file, and in that way they can communicate with one another
- `Dockerfile`'s and `docker-compose.yml` are different things and are meant to co-exist, but it's important to note that `docker-compose.yml` file instructions take precedence over what's in a Dockerfile, so be careful to not override a `Dockerfile`'s instructions if using overlapping functionality in a `docker-compose.yml` file

## Example Work

### Writing the Dockerfile
- First, make sure Docker Desktop (the underlying tech that runs containers) is running so that the Docker engine is started, and log in if need be
- Then, create a `Dockerfile` and, when in the directory containing the `Dockerfile`, build the image with a name tag while looking for the `Dockerfile` in our current directory `.` via `winpty docker build -t test:pandas .`
- Can then run a container based off of this image via `winpty docker run -it test:pandas` to run in in interactive mode (via the `-it` flag)


### Writing the pipeline
- Next, exit the container via `exit` and stop the container if need be via `winpty docker stop <container-id>`
- Then, create a simple test `pipeline.py` and add `COPY pipeline.py pipeline.py` to the `Dockerfile` as well as the current working directory in the image as `WORKDIR /app` to add the file from the source current working directory to the Docker image (with the same file name)
- Then **rebuild** the image via `docker build -t test:pandas .`
- Then start a new container via `docker run -it test:pandas` and notice that you are in the `/app` directory from the `Dockerfile`'s `WORKDIR` argument
- After adding in a new entrypoint of `ENTRYPOINT ["python", "pipeline.py"]` and adding `day = sys.argv[1]` to `pipeline.py`, run `docker run -it test:pandas 2021-01-15`, where the final date is an arg passed to Python

## Reference links
- https://docs.docker.com/desktop/install/windows-install/
- https://docs.docker.com/get-started/
- https://aws.amazon.com/compare/the-difference-between-docker-images-and-containers/
- https://stackoverflow.com/questions/23735149/what-is-the-difference-between-a-docker-image-and-a-container
- https://medium.com/@verazabeida/zoomcamp-2023-week-1-f4f94cb360ae