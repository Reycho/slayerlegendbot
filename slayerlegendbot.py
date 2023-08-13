from pyautogui import *
import pyautogui
import time
import keyboard
import random
import win32api, win32con

time.sleep(10)

count = 0

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(0.1) #This pauses the script for 0.1 seconds
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0 )

def upgrade(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    time.sleep(1) #This pauses the script for 0.1 seconds
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0 )    

def growth():
    click(834, 626)
    time.sleep(0.5)
    upgrade(1190,841)
    time.sleep(0.1)
    click(723,626)

def enchance():
    upgrade(1144,841)
    upgrade(1146,956)
    win32api.SetCursorPos((947,970))
    pyautogui.dragTo(952, 711, 3, button='left')
    upgrade(1144,841)
    upgrade(1144,956)
    pyautogui.dragTo(952, 711, 2, button='left')
    upgrade(1144,841)
    upgrade(1144,956)
    win32api.SetCursorPos((959,795))
    pyautogui.dragTo(959, 984, 1, button='left')
    win32api.SetCursorPos((959,795))
    pyautogui.dragTo(959, 984, 1, button='left')
    
def boss():
    click(1063, 124)
    time.sleep(50)
    click(933, 501)
    click(682, 1047)
    

while keyboard.is_pressed('q') == False:
    
    if pyautogui.pixel(1154, 690)[2] == 182:
        click(1147, 703)
        growth()
        

    time.sleep(120)

    enchance()
    count += 1

    if count == 30:
        boss()
        count = 0

    print(count)
    
    time.sleep(2)

print("Ended")
        
        
        
        


    

    

    

    
