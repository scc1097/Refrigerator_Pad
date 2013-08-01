import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

#defines the database entity type
class Grocery(db.Model):
    item = db.TextProperty(required=True)

#overrides the receive method of the email receiving class
class ReceiveEmail(InboundMailHandler):
    def receive(self,message):
        plaintext = message.bodies('text/plain')
        for text in plaintext:
            txtmsg = ""
            txtmsg = text[1].decode()
            #makes a new database entity with the grocery
            g = Grocery(item=txtmsg, key_name=txtmsg)
            g.put()

application = webapp2.WSGIApplication([
  ReceiveEmail.mapping()
], debug=True)

def main():
    run_wsgi_app(application)
if __name__ == "__main__":
    main()