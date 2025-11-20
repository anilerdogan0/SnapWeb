### OPTIONS
CAPTUREPERIOD = None
LINKLIST = None
BROWSER_WIDTH = None
BROWSER_HEIGHT = None
BROWSER_ZOOM = None

### LIBRARIES
###     ALREADY INSTALLED
import os
import re
import sys
import time
import json
from pathlib import Path
from datetime import datetime as dt
from urllib.parse import urlparse

###     INSTALL NEEDED
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
#pip install selenium

from webdriver_manager.chrome import ChromeDriverManager
#pip install webdriver-manager

### FUNCTIONS
class Snap:
    def init():
        Snap.o(4,"SNAPWEB INIT")
        os.makedirs("SnapWebCaptures", exist_ok=True)
        os.makedirs("SnapWebCookies", exist_ok=True)
        # Check arguments:
        if len(sys.argv) > 1:
            if sys.argv[1] == "-c":
                Snap.browser.cookiemode(sys.argv[2])
                Snap.o(7,"SNAPWEB EXIT")
                sys.exit(0)
        # Check and configure options
        Snap.settings.check()
    def sleeptime(sleeptime_starttime:dt):
        global CAPTUREPERIOD
        sleeptime_totalseconds = CAPTUREPERIOD * 60
        sleeptime_now = dt.now()
        sleeptime_pastinloop = sleeptime_now - sleeptime_starttime
        return sleeptime_totalseconds - int(sleeptime_pastinloop.seconds)
    def cookiename(url):
        cookiemode_url_parsed = urlparse(url)
        cookiemode_url_domain = cookiemode_url_parsed.netloc
        cookiemode_url_domain = cookiemode_url_domain.replace('www.', '')
        cookiemode_url_domain = re.sub(r':\d+', '', cookiemode_url_domain)
        cookiemode_url_domain_safe = re.sub(r'[^a-zA-Z0-9.\-]', '_', cookiemode_url_domain)
        cookiemode_json = f"{cookiemode_url_domain_safe}.json"
        return os.path.join("SnapWebCookies", cookiemode_json)
    def titletofilename(title:str):
        TitleToFilename_now = dt.now()
        return f"SnapWebCaptures/{title}_{TitleToFilename_now.year:04d}-{TitleToFilename_now.month:02d}-{TitleToFilename_now.day:02d}_{TitleToFilename_now.hour:02d}-{TitleToFilename_now.minute:02d}-{TitleToFilename_now.second:02d}.png"
    
    def el(): # EmptyLine
        print()
        Snap.log.write()
    def dl(line:int): # DeleteLine
        for i in range(line):
            print("\x1b[1A\x1b[K",end="")
    def o(type:int, message:str): # Output
        output_timecolor = "\x1b[90m"
        if type == 0: # MESSAGE, Default terminal color (White)
            output_color = "\x1b[39m"
        if type == 1: # SUCCESS, Green
            output_color = "\x1b[32m"
        if type == 2: # PROCESS, Yellow
            output_color = "\x1b[33m"
        if type == 3: # ERROR, Red
            output_color = "\x1b[31m"
        if type in [4,7]: # SnapWeb init and exit text, Blue
            output_color = "\x1b[34m"
        if type not in [0,1,2,3,4,7]:
            return
        Snap.log.write(type, message)
        if type in [4,7]:
            print(f"{output_timecolor}[{Snap.log.timef()}]    {output_color}{message}\x1b[39m")
            if type == 4:
                Snap.el
        if type != 4:
            print(f"\033[1A\033[K{output_timecolor}[{Snap.log.timef()}]    {output_color}{message}\x1b[39m")
        if type != 7:
            print(f"{output_timecolor}Press [Ctrl + C] for stop program.\x1b[39m")
    def i(message:str): # Input
        output_color = "\x1b[35m"
        output_timecolor = "\x1b[90m"
        Snap.log.write(5, message)
        print(f"\033[1A\033[K{output_timecolor}[{Snap.log.timef()}]    {output_color}{message}\x1b[39m")
        inputted = input(f"\x1b[90m[{Snap.log.timef()}]    \x1b[39m")
        if inputted == '':
            print(f"\033[1A\033[K\033[1A")
        Snap.log.write(6, inputted)
        print(f"{output_timecolor}Press [Ctrl + C] for stop program.\x1b[39m")
        return inputted
    
    class browser:
        def is_valid_filename(name_string):
            ILLEGAL_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*]')
            if not name_string or name_string.strip() == "":
                return False
            if ILLEGAL_CHARS_PATTERN.search(name_string):
                return False
            if name_string.endswith('.') or name_string.endswith(' '):
                return False
            if name_string.isspace():
                return False
            return True
        def is_valid_url(url):
            regex = re.compile(
                r'^(?:http)s?://' # http/https protocol
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain
                r'localhost|' # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ip address
                r'(?::\d+)?' # port number
                r'(?:/?|[/?]\S+)$', re.IGNORECASE) # query
            return re.match(regex, url) is not None
        def capture(url, title):
            global BROWSER_HEIGHT, BROWSER_WIDTH, BROWSER_ZOOM
            if os.path.exists(Snap.cookiename(url)):
                cookiefile = Snap.cookiename(url)
                with open(cookiefile, 'r') as file:
                    cookiesdata = json.load(file)
            browseroptions = Options()
            browseroptions.add_argument('--headless=new')
            browseroptions.add_argument('--silent')
            browseroptions.add_argument(f'--window-size={BROWSER_WIDTH},{BROWSER_HEIGHT}')
            browseroptions.add_argument("--disable-notifications")
            browseroptions.add_argument("--disable-gpu")
            driver = webdriver.Chrome(options=browseroptions)
            try:
                driver.get(url)
                if os.path.exists(Snap.cookiename(url)):
                    for cookie in cookiesdata:
                        if 'expiry' in cookie:
                            del cookie['expiry']
                        driver.add_cookie(cookie)
                    driver.refresh()
                driver.execute_script(f"document.body.style.zoom='{BROWSER_ZOOM}%'")
                time.sleep(5)
                thisfilename = Snap.titletofilename(title)
                driver.save_screenshot(thisfilename)
                return thisfilename
            except Exception as e:
                return 0
            finally:
                driver.quit()
        def cookiemode(url):
            jsonname = Snap.cookiename(url)
            options = Options()
            driver = webdriver.Chrome(options=options)
            try:
                driver.get(url)
                Snap.o(1,f"Browser is running. Please sign in your account for cookies.")
                Snap.o(0, f"Press Enter after signed in.")
                input()
                cookiesdata = driver.get_cookies()
                with open(jsonname, 'w') as file:
                    json.dump(cookiesdata, file)
                Snap.o(1, f"Cookies are saved succesfully.")
                input()
            except Exception as e:
                print(f"Cookies couldn't saved! ({e})")
                input()
            finally:
                driver.quit()
            

    class log:

        # Log file variable
        file = None

        # Log filename variable
        name = None

        # Get time and get time formatted
        def time():
            return dt.now()
        def timef(EXTRARG:int = 0):
            now = Snap.log.time()
            if EXTRARG == 1:
                return f"{now.hour:02}_{now.minute:02}_{now.second:02}"
            return f"{now.hour:02}:{now.minute:02}:{now.second:02}"
        # File works
        def open():
            if Snap.log.name is None:
                now = Snap.log.time()
                Snap.log.name = f"SnapWeb {now.year}-{now.month}-{now.day}_{now.hour}-{now.minute}-{now.second}.txt"
            if Snap.log.file is None:
                Snap.log.file = open(Snap.log.name, "a", encoding="utf-8")
            try:
                if Snap.log.file.closed:
                    Snap.log.file = open(Snap.log.name, "a", encoding="utf-8")
            except:
                pass

        def write(type:int = None,message:str = None):
            # Check log file
            if Snap.log.file is None:
                Snap.log.open()
            else:
                try:
                    if Snap.log.file.closed:
                        Snap.log.open()
                    if not Snap.log.file.closed:
                        pass
                except:
                    pass
            # Convert type integer to tags
            if type == 0: # MESSAGE
                tag = "MESSAGE:   "
            if type == 1: # SUCCESS
                tag = "SUCCESS:   "
            if type == 2: # PROCESS
                tag = "PROCESS:    "
            if type == 3: # ERROR
                tag = "ERROR:     "
            if type in [4,7]: # SnapWeb init and exit text
                tag = "           "
            if type == 5: # INPUT QUESTION
                tag = "QUESTION:  "
            if type == 6: # INPUT ANSWER
                tag = "ANSWER:    "
            # Write logs
            if type is None and message is None:
                Snap.log.file.write(f"\n")
            if not type is None and not message is None:
                Snap.log.file.write(f"[{Snap.log.timef()}]  {tag}{message}\n")
    class settings:
        CONFIGURATION = []
        def editcode(configurelist:list):
            global CAPTUREPERIOD, LINKLIST, BROWSER_WIDTH, BROWSER_HEIGHT, BROWSER_ZOOM
            snapwebfilelines = []
            with open(os.path.realpath(__file__), "r", encoding='utf-8') as snapwebfile:
                snapwebfilelines = snapwebfile.readlines()
            if not configurelist[0] == 0:
                snapwebfilelines[1] = f"CAPTUREPERIOD = {configurelist[0]}\n"
                CAPTUREPERIOD = configurelist[0]
            if not configurelist[1] == 0:
                snapwebfilelines[2] = f"LINKLIST = {configurelist[1]}\n"
                LINKLIST = configurelist[1]
            if not configurelist[2] == 0:
                snapwebfilelines[3] = f"BROWSER_WIDTH = {configurelist[2]}\n"
                BROWSER_WIDTH = configurelist[2]
            if not configurelist[3] == 0:
                snapwebfilelines[4] = f"BROWSER_HEIGHT = {configurelist[3]}\n"
                BROWSER_HEIGHT = configurelist[3]
            if not configurelist[4] == 0:
                snapwebfilelines[5] = f"BROWSER_ZOOM = {configurelist[4]}\n"
                BROWSER_ZOOM = configurelist[4]
            with open(os.path.realpath(__file__), "w", encoding='utf-8') as snapwebfile:
                snapwebfile.writelines(snapwebfilelines)
        def check():
            global CAPTUREPERIOD, BROWSER_WIDTH, BROWSER_HEIGHT, BROWSER_ZOOM
            Snap.settings.CONFIGURATION = []
            Snap.el
            if CAPTUREPERIOD is None:
                whileloop = 1
                while(whileloop):
                    enter = Snap.i("Enter time between two capture (minute):")
                    if enter == "":
                        Snap.o(3, "This value is can't be empty! Try again and enter a value.")
                    else:
                        try:
                            enter = int(enter)
                            if enter > 0:
                                Snap.settings.CONFIGURATION.append(enter)
                                whileloop = 0
                            else:
                                Snap.o(3, f"This value is can't be zero or lower! Try again and enter higher value.")
                        except:
                            Snap.o(3, f"This value is not a integer! Try again and enter a integer.")
            else:
                Snap.settings.CONFIGURATION.append(0)
            if not LINKLIST:
                whileloop = 1
                if LINKLIST is None:
                    whilelinklist = []
                else:
                    whilelinklist = LINKLIST.copy()
                while(whileloop):
                    if not whilelinklist:
                        enter = Snap.i("Enter link for capture (with https// or http//):")
                        if enter == "":
                            Snap.o(3,"Need 1 link minimum! Try again and enter a link.")
                        if Snap.browser.is_valid_url(enter):
                            whileloop2 = 1
                            while(whileloop2):
                                enter2 = Snap.i("Enter title for link:")
                                if enter2 == "":
                                    Snap.o(3,"Link title is can't be empty! Try again.")
                                if Snap.browser.is_valid_filename(enter2):
                                    whilelinklist.append(enter2)
                                    whilelinklist.append(enter)
                                    whileloop2 = 0
                                else:
                                    Snap.o(3,"This title is not a valid name.")
                        else:
                            Snap.o(3,"This link is not a valid link.")
                    else:
                        enter = Snap.i("Enter link for capture (leave blank if not want another one)")
                        if enter == "":
                            whileloop = 0
                        if Snap.browser.is_valid_url(enter):
                            whileloop2 = 1
                            while(whileloop2):
                                enter2 = Snap.i("Enter title for link:")
                                if enter2 == "":
                                    Snap.o(3,"Link title is can't be empty! Try again.")
                                if Snap.browser.is_valid_filename(enter2):
                                    whilelinklist.append(enter2)
                                    whilelinklist.append(enter)
                                    whileloop2 = 0
                                else:
                                    Snap.o(3,"This title is not a valid name.")
                        else:
                            Snap.o(3,"This link is not a valid link.")
                Snap.settings.CONFIGURATION.append(whilelinklist)
            else:
                Snap.settings.CONFIGURATION.append(0)
            if BROWSER_HEIGHT is None or BROWSER_WIDTH is None:
                whileloop = 1
                while(whileloop):
                    enter = Snap.i("Enter capture size width (leave blank for use 1080p resolution):")
                    if enter == "":
                        Snap.settings.CONFIGURATION.append(1920)
                        Snap.settings.CONFIGURATION.append(1080)
                        whileloop = 0
                    else:
                        try:
                            enter = int(enter)
                            if enter > 0:
                                Snap.settings.CONFIGURATION.append(enter)
                                while(whileloop):
                                    enter = Snap.i("Enter capture size height:")
                                    if enter == "":
                                        Snap.o(3,"This value is can't be empty! Try again and enter a value.")
                                    else:
                                        try:
                                            enter = int(enter)
                                            if enter > 0:
                                                Snap.settings.CONFIGURATION.append(enter)
                                                whileloop = 0
                                            else:
                                                Snap.o(3,"This value is can't be zero or lower. Try again and enter higher value.")
                                        except:
                                            Snap.o(3,"This value is not a integer! Try again and enter a integer.")
                            else:
                                Snap.o(3, "This value is can't be zero or lower! Try again and enter higher value.")
                        except:
                            Snap.o(3, "This value is not a integer! Try again and enter a integer.")
            else:
                Snap.settings.CONFIGURATION.append(0)
                Snap.settings.CONFIGURATION.append(0)
            if BROWSER_ZOOM is None:
                whileloop = 1
                while(whileloop):
                    enter = Snap.i("Enter browser zoom level (leave blank for use default %100 zoom):")
                    if enter == "":
                        Snap.settings.CONFIGURATION.append(100)
                        whileloop = 0
                    else:
                        try:
                            enter = int(enter)
                            if enter > 0:
                                Snap.settings.CONFIGURATION.append(enter)
                                whileloop = 0
                            else:
                                Snap.o(3, "This value is can't be zero or lower! Try again and enter higher value.")
                        except:
                            Snap.o(3, "This value is not a integer! Try again and enter a integer.")
            else:
                Snap.settings.CONFIGURATION.append(0)
            iflist = [0, 0, 0, 0, 0, 0]
            if Snap.settings.CONFIGURATION == iflist:
                pass
            else:
                Snap.settings.editcode(Snap.settings.CONFIGURATION)


### PROGRAM
try:
    Snap.init()
    while(True): # main loop
        whilestart = dt.now()
        LINKLIST_LENGTH = len(LINKLIST)
        for i in range(0, LINKLIST_LENGTH, 2):
            if i + 1 < LINKLIST_LENGTH:
                if not Snap.browser.is_valid_url(LINKLIST[i+1]):
                    Snap.o(3,"This url is not a valid url!")
                    input()
                    Snap.o(7,"SNAPWEB EXIT")
                    sys.exit(0)
                if not Snap.browser.is_valid_filename(LINKLIST[i]):
                    Snap.o(3,"This title is not a valid name for file!")
                    input()
                    Snap.o(7,"SNAPWEB EXIT")
                    sys.exit(0)
                LinkTitle = LINKLIST[i]
                LinkUrl = LINKLIST[i+1]
                Snap.o(0,f"{LinkTitle}({LinkUrl}) is capturing...")

                SavedFileName = Snap.browser.capture(LinkUrl,LinkTitle)
                Snap.dl(0)
                Snap.o(1, f'The link titled {LinkTitle} was saved as "{SavedFileName}"')
            else:
                Snap.o(3,f'"{LINKLIST[i]}" named titles link is not available.')
        Snap.o(0, f"Waiting for next capture time. ({Snap.sleeptime(whilestart)} seconds)")
        time.sleep(Snap.sleeptime(whilestart))

except KeyboardInterrupt:
    Snap.o(7,"SNAPWEB EXIT")
    sys.exit(0)