
##  This replica of salicicola apps intended for bulk photo entries and must run locally

It contains package (folder with relevant files and subfolders) **photos** and all other needed packages:  
    **names**, **common**, **gisapp**, **photodb**, **gallery** (directory/folder **django4** contains settings for the entire webapp).

Directory/folder **data** contains three SQLite database, two *.xml files (redundant, to be removed in future versions) and the following subfolders:

  * WORK  
     First, create here, if not yet exists, the directory for the current year (or the year when photos were taken)     by following naming convention: NewPhotos{YY}, e.g., NewPhotos24. Copy there the photos to be processed from camera or phone in subdirectory for each day, i.e., all photos taken during the same day must be in the directory named {YYYYMMDD}, e.g., 20240101 for photos taken January 1, 2024.
  
  * RENAME  
     It must contain file *last_number.txt* with last recorded photo number, e.g. if setting it to 0, the first renamed photo will have the number 0001 (e.g., 20240101canon0001.jpg)
  
  * static  
    It contains all supporting static files, such as, Javascript, CSS files.  
    Besides, during processing photos (data entry), smaller scaled version of each photo will be created in subdirectory 'small' (these files can be safely deleted afterwards); thumbnails will be created in subdirectory thm/photos, and photos themselves moved to photos subfolder.
    
  * fixtures  
    Can be empty in case all database tables have been pre-populated (inital account for superuser/administrator: user name: *admin*, password: *admin*). If missing, or to create another one, run (at $APPROOT) `python manage.py createsuperuser` (depending on system settings may need to replace word python by python3).


## Howto
1. For the first stage (renaming photos and extracting GPS Info, if present), [select day in /photos/rename/](/photos/rename) or write date explicitly, e.g., /photos/rename/20240101/
On successfully renaming files it may internally call *update_by_garmin()* (*Current.gpx* file must be present, and contain track for **only** current day), 
and then *redirect to gis app*. On success, the last step will show list of photos with town and if possible location.

2. One may then edit renamed photos, leaving originals intact and edited version named likewise originals adding 'extension', e.g., 20240101canon0001c.jpg

3. For data entry use [/photos/entry/](/photos/entry) and then select right day, or enter day directly, e.g., /photos/entry/20240101/ .
   In the HTML form select correct location (unless it is already selected automatically). Enter any part of plant (or animal) name in corresponding field and select an appropriate name from the drop-down list.
   On entering all photos, you should get the list of entered photos with links to gallery page where one can edit captions, correct location and/or identification if needed (authorization is needed, otherwise, no links would work).

## Important
To avoid manual dealing with numerous dependencies, I would recommend to use dockerized version (get it from Docker Hub as salicicola/photodb_local:latest).
However, in this case, make sure that all files under data/ folder are available and can be added/modified from the host OS. To enable it, use docker-compose or simple docker &amp; bind-mount (create local directory for contents of data/ and populate it with corresponding files from docker's container's, */code/data*). **[See more details here](/howto/docker/)**

## Copyrighted by Salicicola.com
Contents and code released under Creative Commons Attribution-NonCommercial-NoDerivs 4.0 License:
[CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/) 


[Comment ## Todo]::

[Comment detailed instructions needed for using docker]::

[Comment troubleshooting and unfixed bugs]::

[Comment more detailed HOWTO]::
