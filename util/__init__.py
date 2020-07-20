import difflib as dl
import time
def checksimilarity(a, b):
    sim = dl.get_close_matches

    s = 0
    wa = a.split()
    wb = b.split()

    for i in wb:
        if sim(i, wa):
            s += 1

    n = float(s) / float(len(wb))
    return n
def scroll_down(driver):
    j = 0
    try:
        #print("Start scrolling down......")
        while j <= driver.execute_script("return document.body.scrollHeight"):
            j += 250
            driver.execute_script("window.scrollTo(0, " + str(j) + ")")
            time.sleep(0.05)
            #print("Finish scrolling down......")
    except:
        pass