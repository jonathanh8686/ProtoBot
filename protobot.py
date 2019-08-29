
from selenium.webdriver.common.keys import Keys
import subprocess as sp
from selenium import webdriver
import re
import json
import time


driver = webdriver.Chrome()
URL = "http://protobowl.com/hsquizbowl"

driver.get(URL)

time.sleep(2)

found = 0
ts = ""
prevTS = ""
answered = False

answer_mode = True

questions = []

print("Loading question database...")
with open("questions.json", "r") as f:
    for line in f:
        questions.append(json.loads(line))
print("Finished Loading!\n\n")

body = driver.find_element_by_tag_name('body')
while True:
    time.sleep(0.1)
    try:
        now = time.time()
        textSpans = driver.find_elements_by_xpath('//div[contains(@class, "active")]//div[@class="well"]//span[not(contains(@class, "unread")) and not(contains(@class, "inline-icon")) and not(contains(@class, "asterisk"))]')
        questionInfo = driver.find_elements_by_xpath('//div[contains(@class, "active")]//ul[@class="breadcrumb"]//li')

        tournament_info = questionInfo[1].text[:-1].strip()
        
        t_year = tournament_info.split(" ")[0]
        t_name = " ".join(tournament_info.split(" ")[1:])

        ts = ""
        for i in textSpans:
            ts += i.text + " "

        # cancer special cases
        ts = re.sub("^Toss-up #\d+", "", ts, flags=re.IGNORECASE)
        ts = re.sub("^#\d+", "", ts, flags=re.IGNORECASE)
        ts = re.sub("| ", "", ts, flags=re.IGNORECASE)

        if(prevTS not in ts):
            answered = False

        if(answered == False):
            print(ts)
            body.send_keys("n")

            match = []

            for q in questions:
                question_text = q['question'].strip().replace(" (*) ", "")
                if(ts.strip() in question_text and str(t_year) == str(q['year']) and str(t_name) == str(q['tournament'])): 
                    match.append(q)

            
            print(match)
            print("Found " + str(len(match)) + " matches...")

            if(len(match) <= 10):
                for m in match:
                    print(m["answer"])

            pans = ""
            allMatch = True
            for m in match:
                if(pans == ""):
                    pans = m['answer']
                elif(pans != m['answer']):
                    allMatch = False

            if(len(match) == 1 or (allMatch and len(match) > 0)):
                answered = True
                if(answer_mode == True):

                    body.send_keys(" ")

                    ans_text = match[0]['answer']
                    ans_text = re.sub("\[[^>]+\]", "", ans_text)
                    ans_text = re.sub("\([^>]+\)", "", ans_text)
                    ans_text = ans_text.replace("{", "").replace("}", "")

                    print(ans_text)

                    time.sleep(0.2)
                    body.send_keys(ans_text)
                    time.sleep(0.2)
                    body.send_keys(Keys.ENTER)
                    time.sleep(0.5)
                    body.send_keys("n")


            print("\n\n\n")

        found = len(textSpans)
        prevTS = ts

    except:
        print("not found!")
