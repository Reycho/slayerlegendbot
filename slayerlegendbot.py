#have temporarily removed from pyautogui import *
import pyautogui
import time
import keyboard
import json
import win32api, win32con

time.sleep(5)                                #gives user time to clear the screen

width,height = pyautogui.size()
width = width//6                                          #divides screen info into smaller numbers so floats are not needed
height = height//6

count = 0
bossfail = 0  
topcount = 15    

ImageDict = {}
locatedict = {}                                     #stores the location of the buttons
Images = ['boss',
          'expand',
          'growth',
          'money',
          'money2',
          'notreadylevel',
          'plus',
          'plus2',
          'xp',
          'enhance',
          'fail']

def loadImageAssets():
    for im in Images:
        Image = (f"assets/{im}.png")
        ImageDict[im] = Image

def locatebuttons():
    values = [(width*2, height*5, ImageDict['xp']),                      #all the buttons accessible from main page
                (width*2, height*3, ImageDict['growth']),
                (width*3, 0, ImageDict['boss']),
                (width*3, height*4, ImageDict['money']),
                (width*3, height*5, ImageDict['money2']),
                (width*3, height*3, ImageDict['notreadylevel'], True),
                (width*2, height*3, ImageDict['enhance'])]
    
    for value in values:                                   #finds values of all buttons by looping through
        locatecentre(*value)

    x,y = locatedict['growth']                      #a few options located behind button this will happen a few times i wonder if it can be simplified
    click(x,y)

    time.sleep(1)

    locatecentre(width*3, height*4,ImageDict['plus'])
    locatecentre(width*3, height*5,ImageDict['plus2'])

    x,y= locatedict['enhance']
    click(x,y)

    time.sleep(1)      

    with open("location.json", "w") as outfile:           #loads dict into file
        json.dump(locatedict, outfile)       

def locatecentre(x,y,image,grey=False):
    try:
        a, b = pyautogui.locateCenterOnScreen(image, region=(x,y,300,300), grayscale=grey, confidence = 0.85)
        image = image.removesuffix('.png')
        locatedict[image.removeprefix('assets/')] = int(a) , int(b)

    except:
        print(f"Could not locate {image}. Is the app fullscreened?")
    
def click(x,y,z=0.1):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(z) 
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0 )
    
def growth():
    x,y = locatedict['growth']          #upgrades with stat points
    click(x, y)
    time.sleep(0.5)
    x,y = locatedict['plus']
    click(x, y, 1)
    time.sleep(0.1)
    x,y = locatedict['enhance']
    click(x, y)

def upgrade():
    x,y = locatedict['money']
    x,b = locatedict['money2']

    for i in range(3):

        click(x, y, 1)
        click(x, b, 1)

        win32api.SetCursorPos((x-width,b))
        pyautogui.dragTo(x-width, y-(b-y), 3, pyautogui.easeOutQuad, button='left')        #buys upgrades
    
    click(x,b,.5)

    for i in range(2):
        win32api.SetCursorPos((x-width,y))
        pyautogui.dragTo(x-width, b+height, 0.7, pyautogui.easeInQuad, button='left')    #scrolls back up
    
def boss():
    x,y = locatedict['boss']
    click(x, y)                                                             
    time.sleep(35)

    if pyautogui.locateOnScreen('assets/fail.png', region=(width*2, height,500,200), confidence=0.8) != None:     #checks to see if you've succeeded at beating the boss or not
        click(width*3, height*3)
        global bossfail 
        bossfail+=1

    time.sleep(3)
    x,y = locatedict['xp']
    click(x, y)

if pyautogui.pixelMatchesColor(10, 10, (0, 0, 0)) == True:
    try:
        locatecentre(width*3, height*3,ImageDict['expand'])                 #checks to make sure screen is setup properly
        x,y = locatedict['expand']
        click(x, y)
    except KeyError:
        print("Already Expanded")
else:
    print("Bluestacks is not fullscreened")
    exit()

try:
    with open('location.json', 'r') as openfile:      #loads data into dict
        locatedict = json.load(openfile)
        print("Sucessfully loaded file.")

except ValueError:
    loadImageAssets()         #checks to see if file is empty
    locatebuttons()

time.sleep(1)

x,y = locatedict['notreadylevel']

while keyboard.is_pressed('q') == False:

    if pyautogui.pixel(x, y+height//12)[2] == 182:
        click(x, y)
        growth()
    
    time.sleep(240)

    upgrade()
    count += 1

    time.sleep(2)

    if count == topcount:
        boss()
        count = 0

    if bossfail == 2:
        topcount += 3
    
    time.sleep(2)

print("Program Ended")
