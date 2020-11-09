from selenium import webdriver
import random
import time
from datetime import datetime

def match_answer(label):
    if label.find('姓名') != -1:
        return '你的名字'
    elif label.find('学院') != -1:
        return '你的学院'
    elif label.find('专业') != -1:
        return '你的学科'
    elif label.find('年级') != -1:
        return '你的年级'
    elif label.find('电话') != -1:
        return '你的电话'
    elif label.find('号码') != -1:
        return '你的电话'
    elif label.find('联系方式') != -1:
        return '你的电话'
    elif label.find('学号') != -1:
        return '你的学号'

    print('Can not Find Match Answer')
    return ''

def SolveMethon_PC(driver):
    Questions = driver.find_elements_by_css_selector(".div_question")

    if len(Questions) != 0:
        for question in Questions:
            # find question title element
            title  = question.find_element_by_css_selector('.div_title_question')
            # find question input text area element
            inputArea = question.find_element_by_css_selector('textarea')
            # match answer and send to inputArea
            inputArea.send_keys(match_answer(title.text))

        # click submit button
        submitButton = driver.find_element_by_class_name('submitbutton')
        try:
            submitButton.click()
        except:
            print('Submit Failed')
            return False

        # close chrome
        driver.quit()
        print('老婆好感度+1')
        return True
    return False

def SolveMethod_Mobile(driver):
    # find question area
    divQuestion=driver.find_elements_by_xpath("//div[contains(@id,'divQuestion')]")

    if len(divQuestion) != 0:
        # find all question content
        labels   = divQuestion[0].find_elements_by_class_name('field-label')
        # find all question input text area
        elements = divQuestion[0].find_elements_by_class_name('ui-input-text')

        # iteration every question , find match answer, fill it
        for index in range(len(elements)):
            input_text = elements[index].find_element_by_css_selector('input')
            input_text.send_keys(match_answer(labels[index].text))
            index += 1

        # click submit button
        submitButton=driver.find_element_by_css_selector('.voteDiv')
        try:
            submitButton.click()
        except:
            print('Submit Failed')
            return False

        # close chrome
        driver.quit()
        print('老婆好感度+1')
        return True
    return False


# startTime   = datetime(2020, 10, 19, 10, 00, 00)
# questionURL = 'https://www.wjx.top/m/94127374.aspx'

# just for test
startTime   = datetime(2020, 10, 18, 16, 00, 00)
questionURL = 'https://www.wjx.top/jq/94264221.aspx'

# wait until current time is greater than startTime
while datetime.now() < startTime:
    time.sleep(1)

driver = webdriver.Chrome()
driver.get(questionURL)

success = SolveMethon_PC(driver)
if success == False:
    print('can\'t find div_question elements, try to find divQuestion elements')
    success = SolveMethod_Mobile(driver)
    if success == False:
        print('MyGod, Still Failed')