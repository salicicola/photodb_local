## Using Docker Compose

I did not test docker-compose properly, but similar results should be achieved without installing docker-compose separately, by binding the entire /code directory in the container to the appropriate folder in host OS.
For instance using command line, like 
*docker run -i -p 8000:8000 --mount type=bind,src=$HOME/docker_local/code,target=/code/ salicicola/photodb_local*
or filling boxes 'Volumes' similarly in docker-desktop.
(Initially, it would be necessary to copy the entire contents of the /code directory to the folder in the host OS).
This will allow to explore and edit all files in the application.


