from framework import bottle
from framework.bottle import route, template, request, debug, redirect
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail
from re import sub
from google.appengine.ext import db
from time import sleep

#defines all of the database entity types
class Grocery(db.Model):
    item = db.TextProperty(required=True)

class History(db.Model):
    item = db.StringProperty(required=True)

class Pad(db.Model):
    item = db.StringProperty(required=True)
    number = db.StringProperty(required=True)

#function for sending mail
def mail_send(email_subject, email_body):
    mail.send_mail(sender="<contact@refrigeratorpadwebsite.appspotmail.com>",
                   to="<refrigeratorpad@gmail.com>",
                   subject=email_subject,
                   body=email_body)

#all requests to the base url will display the main page
@route('/')
def main_page():
    output = template('templates/main_page')
    return output

#pad menu
@route('/pads')
def pads():
    #checks to see if any pad was updated via http form
    pad_one = request.query.get('item1')
    pad_two = request.query.get('item2')
    pad_three = request.query.get('item3')
    pad_four = request.query.get('item4')
    key_list = [pad_one, pad_two, pad_three, pad_four]

    #if any of the pads were updated
    if pad_one or pad_two or pad_three or pad_four:
        for index, pad in enumerate(key_list): #checks which pad was the one updated
            if pad:
                current_item = pad #the new item is saved in a variable
                number_pad = str(index+1) #the number of the pad is saved
                key = db.Key.from_path('Pad', number_pad)
                new = db.get(key) #fetches the database entity for the pad which was updated
                new.item = current_item #updates the item
                new.put()
                mail_send(number_pad, current_item) #sends email to the Pi
        if current_item not in [history.item for history in db.Query(History, projection=['item'])]: #checks if the item was never used before
            history_entry = History(item=current_item)
            history_entry.put() #add the item to history
        sleep(.25) #puts in a delay to give the website time to update the pads
        redirect('/pads') #redirects back to the base pads url to show changes
    history_list = [] #fetches all of the history entries
    for previous in db.Query(History, projection=['item']):
        history_list.append(previous.item)
    pad_dic = {} #fetches all of the pads data
    for pad in db.Query(Pad, projection=['item', 'number']):
        pad_dic[pad.number] = pad.item
    #displays the pad template with the history and pad data as input
    output = template('templates/pads', data=pad_dic, history_data=history_list)
    return output

#grocery list
@route('/grocery_list')
def grocery_list():
    to_delete = request.query.get('delete')
    #if the user removed something from the grocery list
    if to_delete:
        #delete the database entity and redirect back to the base url
        key = db.Key.from_path('Grocery', to_delete)
        db.delete(key)
        sleep(.25)
        redirect('/grocery_list')
    #requests all of the grocery list database entities
    groceries_list = []
    q = Grocery.all()
    for product in q.run():
        groceries_list.append(product.item)
    #displays the grocery list template with the current groceries as input
    output = template('templates/grocery_list', data=groceries_list)
    return output

def main():
    debug(True)
    run_wsgi_app(bottle.default_app())

if __name__=="__main__":
    main()
