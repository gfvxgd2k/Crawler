# web crawler using python & selenium & google driver
# author : RoyalAzalea
# version 3
#

from selenium import webdriver # need selenium [ pip install selenium ]
import time
import os
import json
import sys
import copy
import urllib.request

# f - write list url to txt file
def write_list_url(url, keyword):
    file_name = keyword + ".txt"
    f = open(file_name, 'w')

    for u in url:
        f.write(str(u) + "\n")

    f.close()

# f - read txt file to list and save img
def read_list_url(keyword):
    global download_path

    file_name = keyword + ".txt"
    f = open(file_name, 'r')

    read = f.read()
    split = read.split("\n")

    read_list = []

    for s in split:
        read_list.append(s)

    # Remove last new-line-character
    read_list.pop()

    # check
    # print(read_list.__len__())
    # for rl in read_list:
    #     print(str(rl))

    f.close()

    # make download dir
    download_path = dir_path + "/" + keyword
    if not os.path.exists(download_path):
        print("make download folder : " + str(download_path))
        os.mkdir(download_path)

    print("------------------------------Start Save Image------------------------------")
    print("image_src_list size : " + str(read_list.__len__()))
    # save image using url
    idx = 0
    for image_url in read_list:
        download_web_image(image_url, idx)
        idx += 1

    print("------------------------------Ebd Save Image------------------------------")

    return read_list



# f - download web image using url
def download_web_image(url, idx):
    global download_path

    if url is None:
        print("Invalid url. idx : " + str(idx))
    else:
        try:
            print(str(idx) + " / try image download : " + url)
            save_path = download_path + "/" + str(idx) + ".jpg"
            opener = urllib.request.URLopener()
            opener.addheader("User-Agent", 'Mozilla/5.0 (Windows; U; Windows NT 5.1;)') # need ! this can allow download through url
            opener.retrieve(url, save_path)
            opener.close()
        except urllib.request.HTTPError as inst:
            output = format(inst)
            print(output)
        except TimeoutError as inst:
            output = format(inst)
            print(output)
        except ConnectionResetError as inst:
            output = format(inst)
            print(output)
        except Exception as inst:
            output = format(inst)
            print(output)

# f - check duplicate url in list(src_object_list)
# type 1 - check between main srcs
# type 2 - check between main src and related src
# type 3 - check between all srcs
def duplicate_check(original_list, type):
    # setting
    output_list = copy.deepcopy(original_list) # need deepcopy
    original_len = len(original_list) # original_list length
    duplicate_count = 0

    if type == 1: # type 1 - check between main srcs
        for idx in range (0, original_len):
            for comp in range(idx + 1, original_len):
                if original_list[idx][0] == original_list[comp][0]:
                    print("Find duplication : Type 1, duplicate_count : " + str(duplicate_count))
                    del output_list[idx - duplicate_count] # delete duplicate object
                    duplicate_count += 1

        # print(output_list)
        return duplicate_check(output_list, 3)

    elif type == 2: # type 2 - check between main src and related src
        for idx in range (0, original_len):
            src_object_len = len(original_list[idx]) # src_object[idx] length
            duplicate_count = 0 # need reset
            for comp in range(1, src_object_len):
                if original_list[idx][0] == original_list[idx][comp]:
                    print("Find duplication : Type 2, duplicate_count : " + str(duplicate_count))
                    del output_list[idx][comp - duplicate_count] # delete duplicate related src
                    duplicate_count += 1

        # print(output_list)
        return duplicate_check(output_list, 3)

    elif type == 3: # type 3 - check between all srcs
        # convert list to set this check between all srcs
        output_set = set([])
        for idx in range(0, original_len):
            temp_s = set(original_list[idx])
            output_set.update(temp_s)

        output_list = list(output_set)
        return output_list

    else:
        print("Invalid Type !")
        return original_list

# f - crawling part saved image url
def crawling(keyword):
    global download_path

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")


    browser = webdriver.Chrome('chromedriver', chrome_options=options)

    browser.implicitly_wait(3)

    search_keyword = keyword  # search

    # make download dir
    download_path = dir_path + "/" + search_keyword
    if not os.path.exists(download_path):
        print("make download folder : " + str(download_path))
        os.mkdir(download_path)


    # open chrome image search
    browser.get("https://images.google.com/")
    time.sleep(1)

    # search query
    query = browser.find_element_by_name("q")
    query.send_keys(search_keyword)
    query.submit()
    time.sleep(3)

    # do pre-setting to get 400 image ( this part number[96, 196, 296] are changeable )
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    thumbnail = browser.find_elements_by_class_name('rg_i')
    thumbnail[96].click()
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    thumbnail = browser.find_elements_by_class_name('rg_i')
    thumbnail[196].click()
    time.sleep(1)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    thumbnail = browser.find_elements_by_class_name('rg_i')
    thumbnail[296].click()
    time.sleep(1)

    # get original image_src
    thumbnail = browser.find_elements_by_class_name('rg_i')
    print("all thumbnail size : " + str(thumbnail.__len__()))
    time.sleep(1)

    # total image src list - 2 dimension
    image_src_list = []

    print("------------------------------Start of Crawling------------------------------")

    # get all image object and make src_object_list [ arch : main - related - related - ... ]
    main_image_search_keyword = 'islir'
    all_main_image = browser.find_elements_by_class_name(main_image_search_keyword)
    print("all main image size : " + str(all_main_image.__len__()))
    for m in range(0, thumbnail.__len__()):
        try:
            temp_src = all_main_image[m].find_element_by_css_selector('img').get_attribute('src')
            src_object_list = []
            src_object_list.append(temp_src)  # get src and append
            image_src_list.append(src_object_list)
        except Exception as ex:
            print("Exception : ", ex )
            continue
    time.sleep(2)

    # append related src to src_object_list
    sol_idx = 0 # src_object_list index
    for t in thumbnail:
        # click thumbnail
        # t.click()
        try:
            browser.execute_script("arguments[0].click();", t)
            time.sleep(2)
        except Exception as ex:
            print("Exception : ", ex)
            continue

        print("@iterator : " + str(sol_idx))

        # get all related class data and append src_object_list
        related_image_panel = 'div[data-hp="imgrc"]' # if you click thumbnail, show up this panel
        related_image_search_keyword = 'islir'
        all_related_image = browser.find_element_by_css_selector(related_image_panel).find_elements_by_class_name(related_image_search_keyword)
        print("all related image size : " + str(all_related_image.__len__()))
        time.sleep(1)
        for ari in all_related_image :
            try:
                temp_src = ari.find_element_by_css_selector('img').get_attribute('src')
                print(temp_src)
                # time.sleep(1)
                image_src_list[sol_idx].append(temp_src)  # get src and append
            except Exception as ex:
                print("Error checking", ex)
                continue

        # increase index
        sol_idx += 1

        # if(sol_idx == 4):
        #     break

    # check
    # print(image_src_list)
    # print(image_src_list.__len__())
    # print(image_src_list[0].__len__())
    # print(image_src_list[1].__len__())
    # print(image_src_list[0])
    # print(image_src_list[1])
    # print(image_src_list[2])
    # print(image_src_list[3])

    # check duplicate src
    ck_type = 2
    print("------------------------------Start Duplicate " + str(ck_type) + " Check ------------------------------")
    image_src_list = duplicate_check(image_src_list, ck_type)
    print("------------------------------End Duplicate " + str(ck_type) + " Check ------------------------------")

    # write list url to txt file
    print("------------------------------Start Write Image url------------------------------")
    write_list_url(image_src_list, keyword)
    print("------------------------------End Write Image url------------------------------")

    print("------------------------------Start Save Image------------------------------")
    print("image_src_list size : " + str(image_src_list.__len__()))
    # save image using url
    idx = 0
    for image_url in image_src_list:
        download_web_image(image_url, idx)
        idx += 1

    print("------------------------------Ebd Save Image------------------------------")

    print("------------------------------End of Crawling------------------------------")
    browser.quit()

# Setting
#chrome_path = 'D:/Devprogram/ChromeDriver/chromedriver.exe' # chrome driver path
dir_path = "download"  # download folder directory path
download_path = "" # downloaded object folder using keywords

# main
keywordlist = ['excavator']


for k in keywordlist:
    crawling(k)
    # read_list_url(k)
