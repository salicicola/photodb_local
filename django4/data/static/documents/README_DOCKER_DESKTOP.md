# HOWTO
## Docker-desktop

**Installation depends on OS and its versions, but usage should be similar in any compatible operating system: Linux, Mac,  Windows (not tested!)** 

  * Install and run docker-desktop [To enlarge image, open in other window using context menu: try right mouse button]![Fig.2](/static/documents/image1.jpg)
  * In search box at the top, write down salicicola or salicicola/photodb-local 
  * Select salicicola/photodb-local (with a tag latest) and press **Run** button.  [Fig.2](/static/documents/image2.jpg)
  
    The image will be downloaded from Docker Hub, and container created.
    The options can be left untouched (may try to type 8000 in the left port box). [Fig.3](/static/documents/image3.jpg)

  * Create directory to keep all data files accessible from OS by current user,   
    e.g., */home/docker/data* (in Windows it would start with *C: or D: ...*)
  * In menu 'Containers', select the current one and then select **Files** tab. 
  * Expand directory */code/* and select subdirectory *data/* 
  * Click it using right mouse button and select 'Save' [Fig.4](/static/documents/image7.jpg)
  * Select the chosen (and already created directory) to keep data files,   
      e.g., /home/docker/data): subdirectory data will be filled with files from running container.
  * Go back to Container's tab, press [] stop button, and then delete it (use ... menu)
  * Go to Images tab and selecting *salicicola/photodb-local:latest*, press *Run* again.
  * In this case type desired port (default 8000), and fill the boxes below:
    The left one with absolute path to data directory (in our example */home/docker/data*   
    and in the right one */code/data* [Fig.5](/static/documents/image8.jpg)
    Then press RUN.
  * That's it. The /*home/docker/data/* directory is ready and contains persistent files.   
    To run next time, just select the same container and press Run.  
  
  **Important Notes:** 

  * Running *rename* first time, may need to edit *data/RENAME/last_number.txt* to set initial photo number, e.g., write 0
  * To update app to a newer version, download and run newer salicicola/photodb-local:latest with the same options, 
    **but do not update */home/docker/data*,** at least do not reset folders **WORK**, **RENAME**, **static/photos**, **static/thm**, and any **database** (*sqlite3) files: this may remove all your saved data.



