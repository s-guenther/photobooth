#! /usr/bin/env python
# -*- coding: utf-8
"""Photobooth Program"""
# The root folder of photobooth.py should contain:
# - photobooth_pictures/
# - dummyslideshow/ with at least 3 pictures (should be photobooth assembly
#                   pictures or at least full hd pictures)
# - discard/

import pygame
import datetime as dt
import RPi.GPIO as GPIO
import time
import os
import shutil
import random
from escpos.printer import Usb
from picamera import PiCamera
from PIL import Image
from PIL import ImageEnhance
from zipfile import ZipFile
from math import ceil

random.seed()

# Some global paths -- set these to desired values
# directory PATH for the event should contain the following files and folders:
# slideshow/
# allpics/
# logo_assembly.png
# logo_partykulaer.png
# logo_print.png
# logo_splash.png
# slideshowbar.png
# background.jpg
PATH = '/home/pi/event'

# some global name tags - Set these to desired Values
S_DATE = '22.06.2019'
S_WHERE_TO_PUT = [u'Zweites Exemplar für uns bitte an die',
                  u'rechte Wand kleben!']


# Some Global Names and paths with should not be set by user
DIRNAME = 'empty'
PICPATH = '/home/pi/photobooth_pictures'
SLIDEPATH = os.path.join(PATH, 'slideshow')
KEEPPATH = os.path.join(PATH, 'allpics')
DISCARDPATH = '/home/pi/discard'

S_WELCOMESCREEN = u'PARTYKULÄR PHOTO BOOTH'
S_MAIL = u'insert.a@mail.adress'

# Dynamic Image Objects
SLIDESHOW = [None]*3
PHOTOS = [None]*5  # Element 0: Assembly, Element 1-4: Photo 1-4

# Static Image Objects
BACKGROUND = pygame.image.load(os.path.join(PATH, 'background.jpg')).convert()

LOGO = pygame.image.load(
    os.path.join(PATH, 'logo_partykulaer.png')).convert_alpha()
_IMGHEIGHT = 110
LOGO = pygame.transform.scale(LOGO, (int(ceil(1089.0/278.0*_IMGHEIGHT)),
                                     _IMGHEIGHT))

SPLASH = pygame.image.load(
    os.path.join(PATH, 'logo_splash.png')).convert_alpha()
_IMGHEIGHT = 200
(_W, _H) = SPLASH.get_size()
SPLASH = pygame.transform.scale(SPLASH, (int(ceil(_W*_IMGHEIGHT/_H)),
                                         _IMGHEIGHT))


# Define States globally
STATE_IDLE = 0
STATE_START = 1
STATE_PHOTO1 = 21
STATE_PHOTO2 = 22
STATE_PHOTO3 = 23
STATE_PHOTO4 = 24
STATE_PHOTO5 = 25
STATE_FINISH = 3
STATE_PRINT_WAIT = 411
STATE_PRINT_FINISH = 412
STATE_ONCEMORE = 42
STATE_PRINT_WAIT_2 = 511
STATE_PRINT_FINISH_2 = 512
STATE_BYE = 6

STATE = STATE_IDLE
STATE_LAST = STATE_BYE


def switch_state(newstate):
    global STATE
    STATE = newstate


def isnewstate():
    global STATE_LAST
    if STATE == STATE_LAST:
        return False
    else:
        STATE_LAST = STATE
        return True


def is_picture_available(picname):
    return os.path.isfile(os.path.join(PICPATH, DIRNAME, picname + '.jpg'))


# Define Timers
class Timer:
    def __init__(self, settime):
        self.__time = settime
        self.__clockstart = time.time()
        
    def starttime(self):
        return self.__time

    def remaining(self):
        return self.__time - (time.time() - self.__clockstart)

    def isfinished(self):
        return self.remaining() < 0

TIMEOUT = Timer(9999)
WAIT = Timer(9999)
CAMTIMER = Timer(9999)
SLIDETIMER = Timer(0)
HIDDEN = Timer(0)


def init_timeout(time_s):
    global TIMEOUT
    TIMEOUT = Timer(time_s)


def init_wait(time_s):
    global WAIT
    WAIT = Timer(time_s)


def init_camtimer(time_s):
    global CAMTIMER
    CAMTIMER = Timer(time_s)


def init_slidetimer(time_s):
    global SLIDETIMER
    SLIDETIMER = Timer(time_s)


def init_hidden(time_s):
    global HIDDEN
    HIDDEN = Timer(time_s)


# noinspection PyUnusedLocal
def buttonleft(channel):
    global STATE
    if STATE == STATE_IDLE:
        STATE = STATE_START
    elif STATE == STATE_START:
        STATE = STATE_PHOTO1
    elif STATE == STATE_PHOTO1:
        pass
    elif STATE == STATE_PHOTO2:
        pass
    elif STATE == STATE_PHOTO3:
        pass
    elif STATE == STATE_PHOTO4:
        pass
    elif STATE == STATE_PHOTO5:
        pass
    elif STATE == STATE_FINISH:
        STATE = STATE_PRINT_WAIT
    elif STATE == STATE_PRINT_WAIT:
        pass
    elif STATE == STATE_PRINT_FINISH:
        STATE = STATE_PRINT_WAIT_2
    elif STATE == STATE_ONCEMORE:
        STATE = STATE_START
    elif STATE == STATE_PRINT_WAIT_2:
        pass
    elif STATE == STATE_PRINT_FINISH_2:
        STATE = STATE_BYE
    elif STATE == STATE_BYE:
        STATE = STATE_START


# noinspection PyUnusedLocal
def buttonright(channel):
    global STATE
    if STATE == STATE_IDLE:
        STATE = STATE_START
    elif STATE == STATE_START:
        STATE = STATE_IDLE
    elif STATE == STATE_PHOTO1:
        STATE = STATE_IDLE
    elif STATE == STATE_PHOTO2:
        STATE = STATE_IDLE
    elif STATE == STATE_PHOTO3:
        STATE = STATE_IDLE
    elif STATE == STATE_PHOTO4:
        STATE = STATE_IDLE
    elif STATE == STATE_PHOTO5:
        STATE = STATE_IDLE
    elif STATE == STATE_FINISH:
        STATE = STATE_ONCEMORE
    elif STATE == STATE_PRINT_WAIT:
        pass
    elif STATE == STATE_ONCEMORE:
        STATE = STATE_IDLE
    elif STATE == STATE_PRINT_WAIT:
        pass
    elif STATE == STATE_PRINT_FINISH_2:
        pass
    elif STATE == STATE_BYE:
        STATE = STATE_IDLE


# noinspection PyUnusedLocal
def buttonstart(channel):
    global STATE
    if STATE == STATE_IDLE:
        STATE = STATE_START
    else:
        STATE = STATE_IDLE


# Define GPIO usage and Buttons

SWITCH1 = 20
SWITCH2 = 16
SWITCHSTART = 21

GPIO.setmode(GPIO.BCM)

GPIO.setup([SWITCH1, SWITCH2, SWITCHSTART], GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(SWITCH1, GPIO.FALLING, callback=buttonleft, bouncetime=300)
GPIO.add_event_detect(SWITCH2, GPIO.FALLING, callback=buttonright, bouncetime=300)
GPIO.add_event_detect(SWITCHSTART, GPIO.FALLING, callback=buttonstart, bouncetime=300)


# Define pygame objects globally

SCREEN = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
CLOCK = pygame.time.Clock()
pygame.font.init()
pygame.mouse.set_visible(False)

CAM = PiCamera()
CAM.resolution = (1920, 1080)
CAM.hflip = False
CAM.vflip = True

PRINTER = Usb(0x0619, 0x0115)  # This depends on your setup

# Define some Colors and Positions

WHITE = (255, 255, 255)
GREY1 = (220, 220, 220)
GREY2 = (150, 150, 150)
BLACK = (0, 0, 0)

LEFT = (60, 900, 850, 180)
RIGHT = (1010, 900, 850, 180)
TLEFT = (485, 1000)
TRIGHT = (1435, 1000)
TMID = (960, 450)


def flip_image(filepath):
    image_obj = Image.open(filepath)
    rotated_image = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
    rotated_image.save(filepath)


def take_picture(name):
    init_camtimer(4)
    CAM.start_preview()
    while not CAMTIMER.isfinished():
        CAM.annotate_text = 'Foto in %1.1f s' % CAMTIMER.remaining()
        time.sleep(0.1)
    CAM.annotate_text = ''
    imgname = os.path.join(PICPATH, DIRNAME, name + '.jpg')
    CAM.capture(imgname, quality=30)
    flip_image(imgname)
    CAM.stop_preview()

def picture_to_globals(pos, name, size=(1280, 720)):
    imgname = os.path.join(PICPATH, DIRNAME, name + '.jpg')
    img = pygame.image.load(imgname)
    img = img.convert()
    img = pygame.transform.scale(img, size)
    PHOTOS[pos] = img


def show_picture(ele, pos=(320, 140)):
    SCREEN.blit(PHOTOS[ele], pos)


def assemble_pictures():
    # Taken and modified from 
    # https://github.com/reuterbal/photobooth/blob/master/photobooth.py
    outer_border = 50
    inner_border = 20
    thumb_box = (960, 540)
    thumb_size = ( thumb_box[0] - outer_border - inner_border ,
                   thumb_box[1] - outer_border - inner_border )

    # Create output image with white background
    output_image = Image.new('RGB', (1920, 1080), BLACK)

    # Image 0
    img = Image.open(os.path.join(PICPATH, DIRNAME, 'pic1.jpg'))
    img.thumbnail(thumb_size)
    offset = ( thumb_box[0] - inner_border - img.size[0] ,
               thumb_box[1] - inner_border - img.size[1] )
    output_image.paste(img, offset)

    # Image 1
    img = Image.open(os.path.join(PICPATH, DIRNAME, 'pic2.jpg'))
    img.thumbnail(thumb_size)
    offset = ( thumb_box[0] + inner_border,
               thumb_box[1] - inner_border - img.size[1] )
    output_image.paste(img, offset)

    # Image 2
    img = Image.open(os.path.join(PICPATH, DIRNAME, 'pic3.jpg'))
    img.thumbnail(thumb_size)
    offset = ( thumb_box[0] - inner_border - img.size[0] ,
               thumb_box[1] + inner_border )
    output_image.paste(img, offset)

    # Image 3
    img = Image.open(os.path.join(PICPATH, DIRNAME, 'pic4.jpg'))
    img.thumbnail(thumb_size)
    offset = ( thumb_box[0] + inner_border ,
               thumb_box[1] + inner_border )
    output_image.paste(img, offset)

    # Logo version SCHWARZ
    logopath = os.path.join(PATH, 'logo_assembly.png')
    img = Image.open(logopath)
    logo_size = (int(ceil(1089.0/278.0*outer_border)), outer_border)
    img.thumbnail(logo_size)
    offset = (1920 - logo_size[0], 1080 - logo_size[1])
    output_image.paste(img, offset)

    # Save assembled image
    output_filename = os.path.join(PICPATH, DIRNAME, 'assembly.jpg')
    output_image.save(output_filename, "JPEG")


def make_print_pic(inname, outname):
    img = Image.open(os.path.join(PICPATH, DIRNAME, inname))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.2)
    img = img.resize((384, int(1080*384/1920)), Image.ANTIALIAS)
    img.save(os.path.join(PICPATH, DIRNAME, outname), "JPEG")


def zip_pics(destiny=KEEPPATH):
    source = os.path.join(PICPATH, DIRNAME)
    files = ['pic1.jpg', 'pic2.jpg', 'pic3.jpg', 'pic4.jpg',
             'crop1.jpg', 'crop2.jpg', 'crop3.jpg', 'crop4.jpg',
             'assembly.jpg']
    with ZipFile(os.path.join(destiny, DIRNAME + '.zip'), 'w') as myzip:
        for mfile in files:
            filepath = os.path.join(source, mfile)
            basename = os.path.basename(filepath)
            myzip.write(filepath, basename)


def print_header():
    logopath = os.path.join(PATH, 'logo_print.png')
    imglogo = Image.open(logopath)
    PRINTER.text('\n')
    PRINTER.image(imglogo)
    PRINTER.text('                      %s' % S_DATE)
    PRINTER.text('\n')


def print_picture_series():
    imagenames = ['crop1.jpg', 'crop2.jpg', 'crop3.jpg', 'crop4.jpg']
    for imgname in imagenames:
        img = Image.open(os.path.join(PICPATH, DIRNAME, imgname))
        PRINTER.image(img)
        PRINTER.text('\n')
        img.close()


def print_footer():
    PRINTER.text('Bilder per Mail? Schicke\n')
    PRINTER.text('    %s\n' % DIRNAME)
    PRINTER.text('als Betreff an\n')
    PRINTER.text(u'    %s\n' % S_MAIL)


def print_pictures():
    print_header()
    print_picture_series()
    PRINTER.text(3*'\n')


def print_pictures_w_anno():
    print_header()
    print_picture_series()
    print_footer()
    PRINTER.text(3*'\n')


# noinspection PyBroadException
def copy_to_remote():
    try:
        commandzip = ('scp ' + os.path.join(KEEPPATH, DIRNAME + '.zip') +
                      ' pi@slide:/home/pi/kept_pics/' +
                      DIRNAME + '.zip')
        commandslide = ('scp ' +
                        os.path.join(PICPATH, DIRNAME, 'assembly.jpg') +
                        ' pi@slide:/home/pi/slideshow/' +
                        DIRNAME + '.jpg')
        os.system(commandzip)
        os.system(commandslide)
    except:
        pass


def put_text(texts, x, y, size=75, color=WHITE):
    if isinstance(texts, str):
        texts = [texts]
    nlines = len(texts)
    ypos = range(nlines)
    ytop = y - (nlines*size + (nlines - 1)*0.0*size)/2
    font = pygame.font.Font(None, size)
    font.set_bold(True)
    for ind in range(nlines):
        ypos[ind] = ytop + ind*size*1.0
    for ind, text in enumerate(texts):
        textobj = font.render(text, 1, color)
        width = textobj.get_width()
        SCREEN.blit(textobj, (x - width/2, ypos[ind]))


def put_timeout():
    put_text(['Timeout in %2.0f s' % TIMEOUT.remaining()], 1830, 20, 32)


def make_dummy_screen(textleft, textright, textmain):
    SCREEN.fill(WHITE)
    # partyculaer logo within text body
    SCREEN.blit(BACKGROUND, (0, 0))
    put_text(textleft, TLEFT[0], TLEFT[1], 75)
    put_text(textright, TRIGHT[0], TRIGHT[1], 75)
    put_text(textmain, TMID[0], TMID[1], 100)


def list_abs_dir(directory):
    # taken and modified from https://stackoverflow.com/questions/9816816
    absfilepaths = list()
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            absfilepaths.append(os.path.abspath(os.path.join(dirpath, f)))
    return absfilepaths


def choose_slideshow_photos():
    # choose 3 elements from slideshow folder
    filelist = list_abs_dir(SLIDEPATH)
    # If there less than 3 elements, take slides from dummyslidepath
    if len(filelist) < 3:
        dummyslides = list_abs_dir('dummyslideshow')
        random.shuffle(dummyslides)
        filelist += dummyslides
        filelist = filelist[0:3]
    random.shuffle(filelist)
    imglist = list()
    for file in filelist:
        img = pygame.image.load(file).convert()
        imglist.append(pygame.transform.scale(img, (640, 360)))
    global SLIDESHOW
    SLIDESHOW = imglist


def make_slideshow():
    SCREEN.blit(SLIDESHOW[0], (0, 500))
    SCREEN.blit(SLIDESHOW[1], (640, 500))
    SCREEN.blit(SLIDESHOW[2], (1280, 500))


# Define Slides

def slide_idle():
    global STATE_LAST
    STATE_LAST = STATE_IDLE
    make_dummy_screen([u'Du kannst auch mich drücken'],
                      ['Oder mich! Nimm mich!'],
                      ['Willkommen in der',
                       '                     PHOTO BOOTH',
                       u'Drücke den roten Start Knopf um ...zu starten',
                       '', '', '', '', '', ''])
    # partykulaer logo within text body
    SCREEN.blit(LOGO, (460, 70))  # see where to put
    # splash logo, party/event name
    SCREEN.blit(SPLASH, (960-_W/2, 375-_H/2))  # see where to put
    put_text([u'Mich hat schon so lange niemand mehr gedrückt =('],
             1440, 1050, 40)
    if HIDDEN.isfinished():
        init_hidden(10)
        CAM.capture(os.path.join('lapse',
                    dt.datetime.now().strftime('%y%m%d%H%M%S') + '.jpg'),
                    resize=(1280, 720), quality=10)
    if SLIDETIMER.isfinished():
        init_slidetimer(10)
        choose_slideshow_photos()
    make_slideshow()


def slide_start():
    if isnewstate():
        init_timeout(60)
        global DIRNAME
        DIRNAME = '%04i' % random.randint(0, 9999)
        while os.path.isdir(os.path.join(PICPATH, DIRNAME)):
            DIRNAME = '%04i' % random.randint(0, 9999)
        os.mkdir(os.path.join(PICPATH, DIRNAME))
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    if HIDDEN.isfinished():
        init_hidden(3)
        CAM.capture(os.path.join('lapse',
                    dt.datetime.now().strftime('%y%m%d%H%M%S') + '.jpg'),
                    resize=(1280, 720), quality=10)
    make_dummy_screen(["Los Geht's!"], ['Lieber doch nicht ...'],
                      ['Es werden 4 Fotos gemacht.',
                       'Schaut in die Kamera!',
                       '',
                       u'Navigieren könnt ihr mit den beiden grauen Knöpfen',
                       'unter dem Bildschirm.',
                       '',
                       u'Viel Spaß!'])
    put_timeout()


def slide_photo1():
    if isnewstate():
        init_wait(3)
    make_dummy_screen([''], ['Abbrechen'], ['Macht euch bereit!'])
    if WAIT.isfinished():
        init_wait(60)
        take_picture('pic1')
        picture_to_globals(1, 'pic1')
        make_dummy_screen([''], [''], [''])
    if is_picture_available('pic1'):
        switch_state(STATE_PHOTO2)


def slide_photo2():
    if isnewstate():
        init_wait(3)
    make_dummy_screen([''], ['Abbrechen'], [''])
    show_picture(1)
    put_text(['Foto 1'], 960, 90, 100)
    pygame.display.flip()
    make_print_pic('pic1.jpg', 'crop1.jpg')
    if WAIT.isfinished():
        init_wait(60)
        take_picture('pic2')
        picture_to_globals(2, 'pic2')
        make_dummy_screen([''], [''], [''])
    if is_picture_available('pic2'):
        switch_state(STATE_PHOTO3)


def slide_photo3():
    if isnewstate():
        init_wait(3)
    make_dummy_screen([''], ['Abbrechen'], [''])
    show_picture(2)
    put_text(['Foto 2'], 960, 90, 100)
    pygame.display.flip()
    make_print_pic('pic2.jpg', 'crop2.jpg')
    if WAIT.isfinished():
        init_wait(60)
        take_picture('pic3')
        picture_to_globals(3, 'pic3')
        make_dummy_screen([''], [''], [''])
    if is_picture_available('pic3'):
        switch_state(STATE_PHOTO4)


def slide_photo4():
    if isnewstate():
        init_wait(3)
    make_dummy_screen([''], ['Abbrechen'], [''])
    show_picture(3)
    put_text(['Foto 3'], 960, 90, 100)
    pygame.display.flip()
    make_print_pic('pic3.jpg', 'crop3.jpg')
    if WAIT.isfinished():
        init_wait(60)
        take_picture('pic4')
        picture_to_globals(4, 'pic4')
        make_dummy_screen([''], [''], [''])
    if is_picture_available('pic4'):
        switch_state(STATE_PHOTO5)


def slide_photo5():
    if isnewstate():
        init_wait(3)
    if WAIT.isfinished():
        switch_state(STATE_FINISH)
    make_dummy_screen([''], ['Abbrechen'], [''])
    show_picture(4)
    put_text(['Foto 4'], 960, 90, 100)
    pygame.display.flip()
    make_print_pic('pic4.jpg', 'crop4.jpg')
    assemble_pictures()
    picture_to_globals(0, 'assembly')
    switch_state(STATE_FINISH)


def slide_finish():
    if isnewstate():
        init_timeout(99)
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    make_dummy_screen([u'Behalten und Exemplar', u'für euch drucken?'],
                      ['Oh Gott, nein,', u'Bitte löscht das!'],
                      [''])
    show_picture(0)
    put_text(['FERTIG!'], 960, 90, 100)
    put_timeout()


def slide_print_wait():
    make_dummy_screen([u''],
                      [''],
                      [''])
    show_picture(0)
    put_text([u'Wenn Druck abgeschlosen: bitte NACH SCHRÄG UNTEN abreißen'],
             960, 90, 60)
    if isnewstate():
        pygame.display.flip()
        shutil.copy(os.path.join(PICPATH, DIRNAME, 'assembly.jpg'),
                    os.path.join(SLIDEPATH, DIRNAME + '.jpg'))
        zip_pics()
        time.sleep(0.2)
        copy_to_remote()
        print_pictures_w_anno()
        init_timeout(60)
        init_wait(1)
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    if WAIT.isfinished():
        switch_state(STATE_PRINT_FINISH)
    put_timeout()


def slide_print_finish():
    if isnewstate():
        init_timeout(60)
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    if HIDDEN.isfinished():
        init_hidden(3)
        CAM.capture(os.path.join('lapse',
                    dt.datetime.now().strftime('%y%m%d%H%M%S') + '.jpg'),
                    resize=(1280, 720), quality=10)
    make_dummy_screen([u'Zweites Exemplar nochmal', u'für uns drucken'],
                      [''],
                      [''])
    show_picture(0)
    put_text(S_WHERE_TO_PUT,
             960, 90, 60)
    put_timeout()


def slide_oncemore():
    if isnewstate():
        zip_pics(DISCARDPATH)
        init_timeout(10)
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    if HIDDEN.isfinished():
        init_hidden(3)
        CAM.capture(os.path.join('lapse',
                    dt.datetime.now().strftime('%y%m%d%H%M%S') + '.jpg'),
                    resize=(1280, 720), quality=10)
    make_dummy_screen([u'Jep, nächster Versuch!'],
                      ['Nein, ich will hier raus!'],
                      ['Nagut, weg damit!',
                       'Nochmal von vorne?'])
    put_timeout()


def slide_print_wait_2():
    make_dummy_screen([u''],
                      [''],
                      [''])
    show_picture(0)
    put_text(S_WHERE_TO_PUT,
             960, 90, 60)
    if isnewstate():
        pygame.display.flip()
        print_pictures()
        init_timeout(60)
        init_wait(1)
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    if WAIT.isfinished():
        switch_state(STATE_PRINT_FINISH_2)
    put_timeout()


def slide_print_finish_2():
    if isnewstate():
        init_timeout(60)
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    if HIDDEN.isfinished():
        init_hidden(3)
        CAM.capture(os.path.join('lapse',
                    dt.datetime.now().strftime('%y%m%d%H%M%S') + '.jpg'),
                    resize=(1280, 720), quality=10)
    make_dummy_screen(['Verstanden!'],
                      [''],
                      S_WHERE_TO_PUT +
                      [u'Bild wieder NACH SCHRÄG UNTEN abreißen.',
                       u'Ihr könnt euch die Bilder auch per Email zusenden',
                       'lassen. Sendet dazu eine Email mit dem Zahlencode',
                       '%s' % DIRNAME,
                       'als Betreff an',
                       '%s' % S_MAIL,
                       u'dann bekommt Ihr diese demnächst zugesendet.'])
    put_timeout()


def slide_bye():
    if isnewstate():
        init_timeout(10)
    if TIMEOUT.isfinished():
        switch_state(STATE_IDLE)
    if HIDDEN.isfinished():
        init_hidden(3)
        CAM.capture(os.path.join('lapse',
                    dt.datetime.now().strftime('%y%m%d%H%M%S') + '.jpg'),
                    resize=(1280, 720), quality=10)
    make_dummy_screen(['Neustart'], [u'Zurück zur Slideshow'],
                      ['Das wars!', '',
                       u'Habt weiterhin viel Spaß auf der Party!'])
    put_timeout()


def main():
    running = True
    while running:
        if STATE == STATE_IDLE:
            slide_idle()
        elif STATE == STATE_START:
            slide_start()
        elif STATE == STATE_PHOTO1:
            slide_photo1()
        elif STATE == STATE_PHOTO2:
            slide_photo2()
        elif STATE == STATE_PHOTO3:
            slide_photo3()
        elif STATE == STATE_PHOTO4:
            slide_photo4()
        elif STATE == STATE_PHOTO5:
            slide_photo5()
        elif STATE == STATE_FINISH:
            slide_finish()
        elif STATE == STATE_PRINT_WAIT:
            slide_print_wait()
        elif STATE == STATE_PRINT_FINISH:
            slide_print_finish()
        elif STATE == STATE_ONCEMORE:
            slide_oncemore()
        elif STATE == STATE_PRINT_WAIT_2:
            slide_print_wait_2()
        elif STATE == STATE_PRINT_FINISH_2:
            slide_print_finish_2()
        elif STATE == STATE_BYE:
            slide_bye()
        pygame.display.flip()
        CLOCK.tick(10)
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
               (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                buttonleft(0)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                buttonright(0)
    pygame.quit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        CAM.close()
