Partykulär Photobooth
=====================

- This is a not well documented, quick and dirty implementation of a raspberry
  pi photobooth
- The code looks awful, but works quite stable
- The following information are a start to set it up for yourself, but don't
  expect them to be complete...


Functionality
-------------

- Programmed for Raspberry Pi
- A pygame based german GUI which leads the photobooth user through the process
- It takes 4 photos and assembles them in a 2x2 matrix with a logo in the right
  bottom corner
- GUI Control via 3 buttons via GPIO pins
- Photos are shot via Raspberry Pi Cam
- Photos are printed via an usb escpos capable thermal printer
- Assembly Photos are displayed on a second screen via a second raspberry pi
- Photos can be send via mail if the user sends a 4 digit code to a certain mail
  adress


Setting it up
-------------

- Copy ./photobooth.py, ./dummyslideshow/ and ./event/ to the HOME directory of
  your pi
- Follow instructions in ./event/README.md
- Copy everything in ./SLIDE_PI/ to the HOME directory of a second pi, follow
  the instructions in ./SLIDE_PI/README.md
- Follow the instructions in the first 40 Lines of ./photobooth.py
- Put ./photobooth.py in autostart at ~/.config/lxsession/LXDE-pi/autostart
- make sure the raspberry pi camera is connected and well setup in the system,
  see the web how to do this
- make sure a thermal printer is connected via usb and capable of the escpos
  protocol and the pi user is allowed to write on it (in the correct groups),
  see the web how to do this
- Connect 3 buttons to the correct GPIO pins and voltage supply GPIO pin. See
  ./photobooth.py for the correct pin numbers.
- make sure all libraries which are imported are installed and working


Todos
-----

- Add comprehensive documentation
- Move to python3 (yes, its still in python2.7)
- Complete rewrite from "Fortran Style State Machine" to sane object oriented
  design


Thanks
------

- ... to a variety of other photobooth implementations found at github or the
  web for inspiration. I'm sorry that I don't know anymore which ones.
- If code is taken directly from other implementations, its remarked as a comment
  in the source code.
