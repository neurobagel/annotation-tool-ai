# Dockerization of the AI Annotation Tool

Since the annotation tool uses ollama to run the LLM it has to be provided by the docker container.
This is done by extending the available [ollama container](https://hub.docker.com/r/ollama/ollama)
For this instructions it is assumed that [docker](https://www.docker.com/) is installed.

## Build the image

The container can be built from the dockerfile available in the repo

```bash
docker build -t annotation-tool-ai .
```
Let's break down the command:

- `docker build`: According to the instructions in the `Dockerfile` this command builds the image.
- `-t `: This flag allows you to name (or tag) an image. 
- `annotation-tool-ai`: This is the nice name for the image

## Run the container from the built image

```bash
docker run -d \
-v ollama:/root/.ollama \
-v /path/to/some/local/folder/:/app/output/  \
--name instance-name annotation-tool-ai
```

Let't break down the command:

- `docker run -d`: The -d flag runs the container in the background without any output in the terminal.
- `-v ollama:root/.ollama`: The -v flag mounts external volumes into the container. In this case the models used within the container are stored locally as well as *Docker volumes* - these are created and managed by Docker itself and is not directly accessible via the local file system.
- `-v /path/to/some/local/folder/:/app/output/`: This is a bind mount (also indicated by the -v flag) and makes a local directory accessible to the container. Via this folder the input and output files (i.e. the `.tsv` input and `.json` output files) are passed to the container but since the directory is mounted also locally accessible. Within the container the files are located in `app/output/`. For more information about Docker volumes vs. Bind mounts see [here](https://www.geeksforgeeks.org/docker-volume-vs-bind-mount/).
- `--name instance-name annotation-tool-ai`: Here you choose a (nice) name for your container from the image we created in the step above.

## Execute the annotation script

The following command runs the script for the annotation process:

```
docker exec -it instance-name python3 full_annotation.py local/input/file local/output/file
```

Let's break down this again:
- `docker exec`: This command is used to execute a command in a running Docker container.
- `-it`: Here are the `-i` and `-t` flag combined which allows for interactive terminal session. It is needed, for example, when you run commands that require input.
- `python3 full_annotation.py local/input/file local/output/file`: This is the command you want to execute in the interactive terminal session within the container. The input file is the to-be-annotated `.tsv` file and the output file is the final `.json` file.

