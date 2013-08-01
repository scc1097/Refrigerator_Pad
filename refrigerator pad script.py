import spidev
from time import sleep
import smtplib
import imaplib
import email
from re import sub

#open an SPI connection
spi = spidev.SpiDev()
spi.open(0,0)

#analog-reads the ADC pin specified by the parameter
#function adopted from code written on jeremyblythe.blogspot.com/2012/09/raspberry-pi-hardware-spi-analog-inputs.html
#read the blog at the above link to learn more about how this function works
def readadc(adcnum):
        r = spi.xfer2([1,(8+adcnum)<<4,0])
        adcout = ((r[1]&3) << 8) + r[2]
        return adcout

#sends email from the pad's Gmail to the website's email with the subject and body specified in the parameters
def send_email(subject, body):
    fromaddr = 'refrigeratorpad@gmail.com'
    toaddrs  = 'groceries@refrigeratorpadwebsite.appspotmail.com'
    msg = "\r\n".join([
        "From: refrigeratorpad@gmail.com",
        "To: %s"%(toaddrs),
        "Subject: %s"%(subject),
        "",
        "%s"%(body)
        ]) #joins the headers into a string


    #login credentials
    username = 'refrigeratorpad'
    password = 'flexiforce'

    # sending the mail
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo
        server.starttls()
        server.login(username,password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
    except:
        print "There was an error."

#checks the email account specified by the first local variable for unread emails from a specified address, and returns a list of tuples containing the subject and body of each email
def read_email():
    username = "refrigeratorpad"
    password = "flexiforce"
    from_address = "contact@refrigeratorpadwebsite.appspotmail.com"
    server = imaplib.IMAP4_SSL("imap.gmail.com",993) #specific gmail server
    server.login(username, password)
    server.select() #opens the main inbox
    command = '(UNSEEN FROM "%s")' %(from_address)
    typ, ids = server.uid('search', None, command) #search for unread emails from the website
    if typ == "OK" and ids[0] != "": #if the request was successful and the return was not empty
        grocery_list = []
        for ident in ids[0].split():
            typ, data = server.uid('fetch', ident, '(RFC822)') #fetch each email that matched the previous requirements
            if typ == "OK":
                data = data[0][1]
                email_message = email.message_from_string(data)
                content = email_message.get_payload()
                content = sub("\r\n", "", content)
                subject = email_message['subject']
                grocery_list.append([subject, content]) #save each pair of subject+body in tuples in a list
            else:
                return "There was a problem fetching the email."
        return grocery_list
    else:
        return "No emails were found."

#defines all of the dictionaries that will be used to store values for the script
sensor_list = ["1", "2", "3", "4"] #this is what is looped through in the main loop
sensors = {"1":0, "2":1, "3":3, "4":2} #defines which ADC pin is assigned to each number sensor
pads = {"1":"empty", "2":"empty", "3":"empty", "4":"empty"} #holds the name of the item on each pad
values = {"1":None, "2":None, "3":None, "4":None} #holds the most recent sensor value for each sensor
empty_counters = {"1":0, "2":0, "3":0, "4":0} #holds the counter for how many times each sensor value is below the threshold without being above the threshold 3 times in a row
full_counters = {"1":0, "2":0, "3":0, "4":0} #holds the counter for how many times in a row the sensor value is above the threshold
threshold = 350 #the threshold which divides empty/near-empty values from heavier values

while True:
    response = read_email() #check for new email
    if type(response)==list: #if there was a new email (it would return a list)
        for i in response: #for each email
            subject = i[0] #subject of the email (which sensor was updated)
            content = i[1] #body of the email (what item was put on the sensor)
            pads[subject] = content #updates the dictionary with what was just put on ty
    for sensor in sensor_list:
        if pads[sensor]!="empty":
            value = readadc(sensors[sensor])
            values[sensor] = value #updates the value of each sensor
            if value < threshold: #read my blog post on my BlueStamp page to learn more about this counter system
                empty_counters[sensor] += 1 #increment the empty counter
                full_counters[sensor] = 0 #reset the full counter
            else: #the value is above the threshold
                full_counters[sensor] += 1 #increment the full counter
            if full_counters[sensor] == 3: #if the sensor is full three times in a row
                empty_counters[sensor] = 0 #reset the empty counter
                full_counters[sensor] = 0 #reset the full counter
            if empty_counters[sensor] == 30: #if the sensor is empty 30 minutes in a row
                send_email("", pads[sensor], "groceries@refrigeratorpadwebsite.appspotmail.com") #send an email to the website
                empty_counters[sensor] = 0 #reset the empty counter
                pads[sensor]="empty" #reset the pad's item
                full_counters[sensor] = 0 #reset the full counter
    sleep(60)