import pyautogui
import time
import json
import win32api, win32con
import schedule
from threading import Event, Thread
import keyboard
from inputimeout import inputimeout, TimeoutOccurred


UserResumed = Event()
User_InputFinished = Event()

# divides screen info into smaller numbers as pyautogui doesn't use floats
xScreenRes, yScreenRes = pyautogui.size()
xSubRegions = xScreenRes // 6  
ySubRegions = yScreenRes // 6

CurrentCount = 0
BossFailCount = 0
MaxCount = 15

data = {}
IconPath = {}
ButtonLocation = {}
TempIcons = []

#removes need to write full address for calling location
def LoadImageAssets(): 
    for ImName in TempIcons:
        Imagepath = f"assets/{ImName}.png"
        IconPath[ImName] = Imagepath


def LocateAllButtons():
    #this button has to be found first and clicked
    try:
        LocateButton(xSubRegions * 7//2, ySubRegions * 3,IconPath["expand"])
        ClickButton("expand")
    except:
        print(
            "Setup Failed, exiting! \n Reminder: For first time setup, click into the character tab and nothing else."
        )
        exit()

    #using xSubRegions and ySubRegions variables to define the area of screen to look in
    buttons = [
    (xSubRegions * 2, ySubRegions * 5, IconPath["xp"]),
    (xSubRegions * 2, ySubRegions * 3, IconPath["growth"]),
    (xSubRegions * 3, 0, IconPath["boss"]),
    (xSubRegions * 3, ySubRegions * 4, IconPath["money"]),
    (xSubRegions * 3, ySubRegions * 5, IconPath["money2"]),
    (xSubRegions * 3, ySubRegions * 3, IconPath["notreadylevel"]),
    (xSubRegions * 2, ySubRegions * 3, IconPath["enhance"]),
    (xSubRegions * 5 // 2, ySubRegions * 5, IconPath["equip"]),
    (xSubRegions * 2, ySubRegions * 3, IconPath["accessory"]),
    (xSubRegions * 2, ySubRegions * 4, IconPath["sword"]),
    (xSubRegions * 2, ySubRegions * 3, IconPath["weapon"]),
    (xSubRegions * 7 // 2, ySubRegions * 3 // 2, IconPath["next"]),
    (xSubRegions * 5 // 2, ySubRegions * 4, IconPath["combinebig"]),
    (xSubRegions * 5 // 2, ySubRegions * 5, IconPath["close"])
    ]
    # finds buttons of all buttons by looping through, seperated into 3 seperate times as some buttons exists in different menus
    buttons1 = buttons[:8]
    for button in buttons1:  
        LocateButton(*button)

    #this ClickButton function and the ones below open a new menu
    ClickButton("growth")      
    LocateButton(xSubRegions * 3, ySubRegions * 4, IconPath["plus"])
    LocateButton(xSubRegions * 3, ySubRegions * 5, IconPath["plus2"])

    ClickButton("enhance")
    ClickButton("equip")
    buttons2 = buttons[8:11]
    for button in buttons2:
        LocateButton(*button)

    ClickButton("sword")

    LocateButton(xSubRegions * 3, ySubRegions // 2, IconPath["combine"])

    ClickButton("combine")

    buttons3 = buttons[11:14]
    for button in buttons3:
        LocateButton(*button)
    
    #resets back to default
    ClickButton("close")
    ClickButton("xp")


def LocateButton(xLocation, yLocation, iconpath): 
    try:
        xvalue2, yvalue2 = pyautogui.locateCenterOnScreen(
            iconpath, region=(xLocation, yLocation, 500, 500), confidence=0.85
        )
        #removes need to write full address everytime when calling ButtonLocation
        iconname = iconpath.removesuffix(".png")
        ButtonLocation[iconname.removeprefix("assets/")] = int(xvalue2), int(yvalue2)    

    except:
        print(f"Could not locate {iconpath}. Is the app fullscreened?")
        exit()


def ClickButton(image, z=0.1):
    xvalue, yvalue = ButtonLocation[image]
    win32api.SetCursorPos((xvalue, yvalue))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(z)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(0.2)

# upgrades with stat points
def UpgradeCharacter():  
    ClickButton("growth")
    ClickButton("plus", 1)
    ClickButton("enhance")

#upgrades stats with money
def UpgradeStats(): 
    #xvalue value is the same for both
    xvalue, yvalue = ButtonLocation["money"]
    xvalue, yvalue2 = ButtonLocation["money2"]

    for i in range(3):
        ClickButton("money", 1)
        ClickButton("money2", 1)

        win32api.SetCursorPos((xvalue - xSubRegions, yvalue2))
        pyautogui.dragTo(
            xvalue - xSubRegions, yvalue - (yvalue2 - yvalue), 3, pyautogui.easeOutQuad, button="left"
        ) 

    ClickButton("money2", 0.5)
    # scrolls back up
    for i in range(2):
        win32api.SetCursorPos((xvalue - xSubRegions, yvalue))
        pyautogui.dragTo(
            xvalue - xSubRegions, yvalue2 + ySubRegions, 0.7, pyautogui.easeInQuad, button="left"
        )  
        time.sleep(0.3)

#attempt level clear
def BossAttempt(): 
    ClickButton("boss")
    time.sleep(35)

    # checks to see if you've succeeded at beating the boss or not
    if (
        pyautogui.locateOnScreen(
            "assets/fail.png", region=(xSubRegions * 2, ySubRegions, 500, 200), confidence=0.8
        )
        != None
    ):  
        ClickButton("next")
        global BossFailCount
        BossFailCount += 1    
        time.sleep(3)

    ClickButton("xp")


#main loop
def MainLoop():
    global CurrentCount
    global MaxCount
    xvalue, yvalue = ButtonLocation["notreadylevel"]
    while 1:
        #checks to see if you've levelled up
        if pyautogui.pixel(xvalue, yvalue + ySubRegions // 12)[2] == 182: 
            ClickButton("notreadylevel")
            UpgradeCharacter()
        #checks to see if pause has been called
        schedule.run_pending()

        UpgradeStats()
        CurrentCount += 1

        schedule.run_pending()

        if CurrentCount == MaxCount:
            BossAttempt()
            CurrentCount = 0
        #increments number of loops before another boss attempt if you fail twice in a row
        if BossFailCount == 2:
            MaxCount += 3    
        #this loop checks for new inputs while still giving time for money to build up
        for i in range(16):
            schedule.run_pending()
            time.sleep(15)


def UserInput():
    #these .is_set() conditions allow temination of the loop from anywhere in the file
    while not User_InputFinished.is_set(): 
        match input(
            "Type 'p' for Pause, or 'stop' to end the program, or 'reset' to refind button locations. Note: Give the program some time to pause. \n> "
        ):
            case "p":
                # schedules pause at the next end of loop
                TimeScheduled = TimeNow()
                schedule.every().day.at(TimeScheduled).do(
                    Pause
                )  
                print("Input received")
                #waits till user resumes
                while not UserResumed.is_set():
                    time.sleep(0.5)
                #clears schedule just in case
                schedule.clear()
                User_InputFinished.set()
            case "stop":
                print("Stopping Program")  
                exit()
            case "reset":
                SetupDone = ["False"]
                data["Loaded"] = SetupDone
                # loads data into file
                with open("data.json", "w") as outfile:  
                    json.dump(data, outfile)
                exit()
            case _:
                print("Invalid Input!")

def DefaultPage():
    ClickButton("close")
    #checks to see if you're already on the right screen
    if (
        pyautogui.locateOnScreen(
            "assets/money.png", region=(xSubRegions * 3, ySubRegions * 4, 400, 400), confidence=0.8
        )
        == None
    ): 
        ClickButton("xp")
    # all code below is to DefaultPage current menu to default
    ClickButton("enhance")

    xvalue, yvalue = ButtonLocation["money"]
    xvalue, yvalue2 = ButtonLocation["money2"]

    for i in range(2):
        win32api.SetCursorPos((xvalue - xSubRegions, yvalue))
        pyautogui.dragTo(
            xvalue - xSubRegions, yvalue2 + ySubRegions, 0.7, pyautogui.easeInQuad, button="left" #scrolls back up
        )


#this spaghetti code returns current time + 1 minute
def TimeNow(): 
    TimeNow = (time.localtime())  
    # grabs 1 minute ahead of current time so scheduler works
    TimeNowHr = time.strftime("%H", TimeNow)
    TimeNowMin = time.strftime("%M", TimeNow)
    TimeScheduleMin = int(TimeNowMin) + 1
    # time module gives time as 12:9 if minutes is below 10
    if (int(TimeScheduleMin) <= 9):  
        TimeScheduleMin = f"0{TimeScheduleMin}"

    elif(TimeScheduleMin==60):
        TimeScheduleMin = 0
        TimeNowHr = int(TimeNowHr) + 1

    TimeScheduled = f"{TimeNowHr}:{TimeScheduleMin}"
    return TimeScheduled


def Pause():
    print("Paused! Hold 'q' to resume.")
    #Thread(target=ac).start()  #see ac function 
    #waits until q is pressed
    while keyboard.is_pressed("q") == False:
        time.sleep(0.5)
        
    # stops ac function
    UserResumed.set()  
    print("Resumed!")

# claims attendence reward
def ClaimAttendence():
    xvalue2, yvalue2 = pyautogui.locateCenterOnScreen(
        "assets/claim.png", region=(xSubRegions * 2, ySubRegions * 4, 600, 300), confidence=0.8
    )  
    win32api.SetCursorPos((xvalue2, yvalue2))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(1)
    DefaultPage()

#this is all commented out because it doesn't work
# def ac():
#     while not UserResumed.is_set():
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
#     ClickButton("equip")
#     ClickButton(which)
#     ClickButton("sword")
#     ClickButton("combine")

#     for i in range(23):
#         ClickButton("combinebig")
#         ClickButton("next")

#SecondaryLoop loop for user input
def SecondaryLoop(): 
    while 1:
        UserInput()  
        time.sleep(10)
        # resets events so loops run 
        UserResumed.clear() 
        User_InputFinished.clear()
        DefaultPage()

with open("data.json", "r") as openfile:  
    data = json.load(openfile)

SetupDone = data.get("Loaded")

#checks to see if locations of buttons has been found before
if SetupDone[0] == 'True':  
    print("Sucessfully loaded file.")
    ButtonLocation = data["ButtonLocation"] 
    time.sleep(5)
    ClickButton("expand")  
else: 
    #runs setup code
    print("Reminder: For first time setup, ClickButton into the character tab and nothing else.")
    time.sleep(10)
    TempIcons = data.get("Images")
    LoadImageAssets()
    LocateAllButtons()
    SetupDone = ["True"]
    #organises everything into one dictionary
    data["Images"] = TempIcons
    data["ButtonLocation"] = ButtonLocation
    data["Loaded"] = SetupDone
    with open("data.json", "w") as outfile:
        json.dump(data, outfile)

 # checks to make sure screen is setup properly
if (
    pyautogui.pixelMatchesColor(10, 10, (0, 0, 0)) == False
): 
    print("Bluestacks is not fullscreened")
    exit()

schedule.every().day.at("00:00").do(ClaimAttendence) #this is so at midnight bot is not interrupted by mandatory login reward

Thread(target=MainLoop).start()
Thread(target=SecondaryLoop).start()
