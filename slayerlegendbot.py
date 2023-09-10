import pyautogui
import time
import json
import win32api, win32con
import schedule
from threading import Event, Thread
import keyboard
from inputimeout import inputimeout, TimeoutOccurred


finishsleep = Event()
inputasked = Event()

# divides screen info into smaller numbers as pyautogui doesn't use floats
width, height = pyautogui.size()
width = width // 6  
height = height // 6

count = 0
bossfail = 0
topcount = 15

data = {}
ImageDict = {}
locatedict = {}
Images = []

 #removes need to write full address for calling location
def loadImageAssets(): 
    for im in Images:
        Image = f"assets/{im}.png"
        ImageDict[im] = Image


def locatebuttons():
    try:
        locatecentre(width * 7//2, height * 3,ImageDict["expand"])
        click("expand")
    except:
        print(
            "Setup Failed, exiting! \n Reminder: For first time setup, click into the character tab and nothing else."
        )
        exit()
    values = [ #using width and height variables so this code works across all screen resolutions (same or close aspect ratio)
    (width * 2, height * 5, ImageDict["xp"]),
    (width * 2, height * 3, ImageDict["growth"]),
    (width * 3, 0, ImageDict["boss"]),
    (width * 3, height * 4, ImageDict["money"]),
    (width * 3, height * 5, ImageDict["money2"]),
    (width * 3, height * 3, ImageDict["notreadylevel"]),
    (width * 2, height * 3, ImageDict["enhance"]),
    (width * 5 // 2, height * 5, ImageDict["equip"]),
    (width * 2, height * 3, ImageDict["accessory"]),
    (width * 2, height * 4, ImageDict["sword"]),
    (width * 2, height * 3, ImageDict["weapon"]),
    (width * 7 // 2, height * 3 // 2, ImageDict["next"]),
    (width * 5 // 2, height * 4, ImageDict["combinebig"]),
    (width * 5 // 2, height * 5, ImageDict["close"])
    ]
    values1 = values[:8]
    for value in values1:  # finds values of all buttons by looping through, seperated into 3 seperate times as some buttons exists in different menus
        locatecentre(*value)

    click("growth")      #this and the ones below  open a new menu

    locatecentre(width * 3, height * 4, ImageDict["plus"])
    locatecentre(width * 3, height * 5, ImageDict["plus2"])

    click("enhance")
    click("equip")
    values2 = values[8:11]
    for value in values2:
        locatecentre(*value)

    click("sword")

    locatecentre(width * 3, height // 2, ImageDict["combine"])

    click("combine")

    values3 = values[11:14]
    for value in values3:
        locatecentre(*value)

    click("close")
    click("xp")


def locatecentre(x, y, image): #function to find where a button is
    try:
        a, b = pyautogui.locateCenterOnScreen(
            image, region=(x, y, 500, 500), confidence=0.85
        )
        image = image.removesuffix(".png")
        locatedict[image.removeprefix("assets/")] = int(a), int(b)    #removes need to write full address everytime when calling locatdict

    except:
        print(f"Could not locate {image}. Is the app fullscreened?")
        exit()


def click(image, z=0.1):
    x, y = locatedict[image]
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(z)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(0.2)


def growth():  # upgrades with stat points
    click("growth")
    time.sleep(0.5)
    click("plus", 1)
    time.sleep(0.1)
    click("enhance")
    time.sleep(2)


def upgrade(): #upgrades stats with money
    x, y = locatedict["money"]
    x, b = locatedict["money2"]

    for i in range(3):
        click("money", 1)
        click("money2", 1)

        win32api.SetCursorPos((x - width, b))
        pyautogui.dragTo(
            x - width, y - (b - y), 3, pyautogui.easeOutQuad, button="left"
        )  # buys upgrades

    time.sleep(2)

    click("money2", 0.5)

    for i in range(2):
        win32api.SetCursorPos((x - width, y))
        pyautogui.dragTo(
            x - width, b + height, 0.7, pyautogui.easeInQuad, button="left"
        )  # scrolls back up


def boss(): #attempt level clear
    click("boss")
    time.sleep(35)

    schedule.run_pending()

    if (
        pyautogui.locateOnScreen(
            "assets/fail.png", region=(width * 2, height, 500, 200), confidence=0.8
        )
        != None
    ):  # checks to see if you've succeeded at beating the boss or not
        click("next")
        global bossfail
        bossfail += 1

    time.sleep(3)

    click("xp")


def reset():
    click("close")
    if (
        pyautogui.locateOnScreen(
            "assets/money.png", region=(width * 3, height * 4, 400, 400), confidence=0.8
        )
        == None
    ): #checks to see if you're already on the right screen
        click("xp")
      # all code below is to reset current screen
    click("enhance")

    x, y = locatedict["money"]
    x, b = locatedict["money2"]

    for i in range(2):
        win32api.SetCursorPos((x - width, y))
        pyautogui.dragTo(
            x - width, b + height, 0.7, pyautogui.easeInQuad, button="left" #scrolls back up
        )


def attendence():
    a, b = pyautogui.locateCenterOnScreen(
        "assets/claim.png", region=(width * 2, height * 4, 600, 300), confidence=0.8
    )  # claims attendence reward
    win32api.SetCursorPos((a, b))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(1)
    reset()


def update():  #main loop
    global count
    global topcount
    x, y = locatedict["notreadylevel"]
    while 1:
        if pyautogui.pixel(x, y + height // 12)[2] == 182: #checks to see if level up button is ready
            click("notreadylevel")
            growth()
        schedule.run_pending()

        upgrade()
        count += 1

        schedule.run_pending()

        time.sleep(2)

        if count == topcount:
            boss()
            count = 0

        if bossfail == 2:
            topcount += 3   #increments number of loops before another boss attempt if you fail twice in a row
        for i in range(16): #this loop checks for new inputs while still giving time for money to build up
            schedule.run_pending()
            time.sleep(15)


def whatisthetime(): #this spaghetti code returns current time + 1 minute
    whatisthetime = (
        time.localtime()
    )  # grabs 1 minute ahead of current time so scheduler works
    current_timehr = time.strftime("%H", whatisthetime)
    current_timemin = time.strftime("%M", whatisthetime)
    current_timemin = int(current_timemin) + 1
    if (
        int(current_timemin) <= 9
    ):  # time module gives time as 12:9 if minutes is below 10
        current_timemin = f"0{current_timemin}"
    timepause = f"{current_timehr}:{current_timemin}"
    return timepause


def pause():
    print("Paused! Hold 'q' to resume.")
    #Thread(target=ac).start()  #see ac function
    while keyboard.is_pressed("q") == False: #waits until q is pressed
        time.sleep(0.5)

    finishsleep.set()  # stops ac function
    print("Resumed!")


def user_input():
    while not inputasked.is_set(): #these .is_set() conditions allow temination of the loop from anywhere in the file
        match input(
            "Type 'p' for pause, or 'stop' to end the program, or 'reset' to reset to refind button locations. Note: Give the program some time to pause. \n> "
        ):
            case "p":
                timepause = whatisthetime()
                schedule.every().day.at(timepause).do(
                    pause
                )  # schedules pause at the next end of loop
                print("Input received")
                while not finishsleep.is_set():
                    time.sleep(0.5)
                schedule.clear()
                inputasked.set()
            case "stop":
                print("Stopping Program")  # ends main while loop
                time.sleep(3)
                exit()
            case "reset":
                check = ["False"]
                data["Loaded"] = check
                with open("data.json", "w") as outfile:  # loads data into file
                    json.dump(data, outfile)
                exit()
            case _:
                print("Invalid Input!")

#this is all commented out because it doesn't work
# def ac():
#     while not finishsleep.is_set():
#         try:
#             acinput = inputimeout(
#                 prompt="Type 'sword' or 'accessory' for the respective autocombines.  This will automatically close.\n >> ",
#                 timeout=10,
#             )
#             match acinput:
#                 case "sword":
#                     autocombine("weapon")
#                 case "accessory":
#                     autocombine("accessory")
#                 case _:
#                     print("Invalid answer")
#         except TimeoutOccurred:
#             print("Wait")  # what do I put here


# def autocombine(which):
#     click("equip")
#     click(which)
#     click("sword")
#     click("combine")

#     for i in range(23):
#         click("combinebig")
#         click("next")


def secondary(): #secondary loop for user input
    while 1:
        user_input()  
        time.sleep(10)
        finishsleep.clear() # resets events so loops run 
        inputasked.clear()
        reset()
        time.sleep(2)


with open("data.json", "r") as openfile:  # loads data into dict
    data = json.load(openfile)

Images = data.get("Images")
check = data.get("Loaded")

if check[0] == 'True':  #checks to see if locations of buttons has been found before
    print("Sucessfully loaded file.")
    locatedict = data["locatedict"] 
    time.sleep(5)
    click("expand")  
else: #runs setup code
    print("Reminder: For first time setup, click into the character tab and nothing else.")
    time.sleep(10)
    loadImageAssets()
    locatebuttons()
    check = ["True"]
    data["Images"] = Images
    data["locatedict"] = locatedict
    data["Loaded"] = check
    with open("data.json", "w") as outfile:  # loads data into file
        json.dump(data, outfile)

if (
    pyautogui.pixelMatchesColor(10, 10, (0, 0, 0)) == False
):  # checks to make sure screen is setup properly
    print("Bluestacks is not fullscreened")
    exit()

time.sleep(5)

schedule.every().day.at("00:00").do(attendence) #this is so at midnight bot is not intterupted by mandatory login reward

Thread(target=update).start()
time.sleep(2)
Thread(target=secondary).start()
