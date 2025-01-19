# Learn Kestra


##  Kestra
- GitHub repo: https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration
- Kestra documentation: https://go.kestra.io/docs
- Kestra has videos such as a 15-minute "Getting Started" video (https://www.youtube.com/watch?v=a2BZ7vOihjg), a tutorial series, and installation guides (such as with Docker Compose) on their YouTube channel: https://www.youtube.com/@kestra-io
- To install, see: https://kestra.io/docs/getting-started/quickstart


## Getting Started
- **Kestra** is an *event-driven* data orchestration platform with an intuitive UI and many optional plugins
- To start, download the Docker image and run it in a Docker container via `winpty docker run --pull=always --rm -it -p 8080:8080 --user=root -v //var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp kestra/kestra:latest server local`
    - *NOTE*: You need a double forward slash `//` before the local directory of the volume (`-v` argument) for some reason (maybe just on Windows OS?)
- Then, open `http://localhost:8080` in a browser window to launch the Kestra UI and start building **flows**
