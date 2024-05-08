
## Command-line docker @ Linux

  * Install docker (e.g., in Debian-based Linux, including Ubuntu, Mint, etc., run *sudo apt install docker*)
  * Optionally, add current user to docker group, that will allow to run docker without sudo: *sudo usermod -a -G docker $USER*
  * Run *sudo docker run -ip 8000:8000 salicicola/photoodb_local:latest*  
    (If port 8000 is in use, try any other, e.g., 8888:8888). This will download the salicicola/photoodb_local:latest image, create container and run it. On seeing the message, *Quit the server with CONTROL-C*, may open any browser with url [http://localhost:8000/docker](http://localhost:8000/docker) (or other port) to see this file. However, the app is yet useless since one may not add new photos (the directory */data/* is not easily available from the host Linux.)  
  * Prepare directory to keep all photos and other static files, e.g., in other terminal run *mkdir ~/docker_local* . This will create folder *docker_local/* in your home directory
  * In the same or other terminal window run *sudo docker ps*
  
    You will see something like
 
    *CONTAINER_ID   IMAGE  COMMAND  CREATED  STATUS  PORTS   NAMES*

    *0e5c7d5d9ad   salicicola/photodb_local:latest   "python manage.py ru…"   2 minutes ago   ...*  

    (I accidently close the running app, second line will be empty: in such case, just run *sudo docker ps --all*)  

  * Run command *sudo docker cp 60e5c7d5d9ad:/code/data* $HOME/docker_local (replace container_id value and target directory as needed; hint: to copy/paste text inside terminal willow, use Shift-Ctrl-C and Shift-Ctrl-V).
    If no error message appears, the directory $HOME/docker_local/data will be filled by numerous files including SQLite DB files, etc.
  * To ensure that $HOME/docker_local is not write protected, try running command *sudo chown -Rv $USER:$USER $HOME/docker_local  
    (this will change the owner of all files there to current user, if necessary)
  * Close the running server (in first termnal window press Ctrl-C and close terminal).
  * In other terminal window run command  
    *sudo docker run -i -p 8000:8000 --mount type=bind,src=$HOME/docker_local/data,target=/code/data salicicola/photodb_local*

    Use the same command in a future, the contents of *$HOME/docker_local/data* will now be persistent, and you may start adding and processing new photos (be sure to set initial photo number in *$HOME/docker_local/data/RENAME/last_number.txt*, e.g., to 0

   * For convenience, copy the previous command to a file, e.g., *run_docker.sh* and use it as follows *. run_docker.sh* (it's usualy recommended to make the file executable, in which case it can be run as *./run_docker.sh*;   
     naturally, the working directory should be the one containing *run_docker.sh*).
   



