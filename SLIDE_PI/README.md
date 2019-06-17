Setting up slideshow raspberry pi
---------------------------------

- The content of this folder goes to a separate raspberry pi
- Move everything inside to a HOME folder
- create a /kept_pics and a /slideshow folder


Setting up slideshow
--------------------

- The /dummyslideshow folder should contain 2-5 pictures. These will be
  displayed as long as there are not enough pictures from the current/new event
- to initialize a new event, execute ~/move_event.py <old_event_name>. This will
  move all pictures from ~/slideshow to ~/old_event_name and copy all pictures
  from ~/dummyslideshow to ~/slideshow
- put ~/start_feh in ~/.config/lxsession/LXDE-pi/autostart and
  ~/watch_slideshow_folder.py in /etc/rc.local to get them executed at startup;
  the first one shows the pictures in ~/slideshow in fullscreen and the second
  one kicks out dummyslideshow pictures as soon as ~/slideshow folder gets
  filled by pictures of the new event


Sending mails
-------------

- put ~/send_photos.py in /etc/rc.local autostart
- fill in your server credentials in send_photos.py --> the global variables
  USER, PASSWORD, IMAPSERVER, SMTPSERVER after the import statements


Communication between raspberry pis
-----------------------------------

- The slideshow raspberry must be found by the photobooth raspberry pi
- To do so - the slideshow pi must be known to the photobooth pi as "slide" in
  /etc/hosts
- ssh certificates must be exchanged so allow ssh/scp connections without
  password
