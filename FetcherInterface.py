import cgi
import ImageFetcher

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import mail

class StartPage(webapp.RequestHandler):
        def get(self):
            '''
            Acts as the landing page, where the user can specify the parameters for the program to utilize.
            '''
            user = users.get_current_user()
            if user:
                self.response.out.write("""
                <html>
                <body>
                    <form action="/results" method="post">
                        <div><input type="text" size="50" name="SourceSite"/>Source Website</div>
                        <div><input type="text" name="MaxFetchSize"/>Max Images (optional)</div>
                        <div><input type="text" name="AttachSize" value="5"/>Images per email</div>
                        <div><input type="submit" value="Fetch Images"></div>
                        <div>Click the "Fetch" button and the images will be emailed to your account.</div>
                    </form>
                </body>
                </html>""")
            else:
                self.redirect(users.create_login_url(self.request.uri))

class ResultsPage(webapp.RequestHandler):
    def post(self):
        '''
        A rather bland page that just lets the user know the email is on its way.
        '''
        sourceSite = ""+cgi.escape(self.request.get('SourceSite'))
        if not sourceSite.startswith('http://'):
            sourceSite = 'http://'+sourceSite
        try:
            limit = int(""+self.request.get('MaxFetchSize'))
        except ValueError:
            limit = -1
        try:
            attachSize = int(""+self.request.get('AttachSize'))
        except ValueError:
            attachSize = 5
            
        source = ImageFetcher.returnSource(sourceSite)
        images = ImageFetcher.findImages(source)
        ResultsPage.processImages(self,sourceSite,images,limit,attachSize)
        self.response.out.write('<html><body>Your images are being collected, and will be emailed to you momentarily.  Please wait...')
        self.response.out.write('</body></html>')
        
    def processImages(self,sourceSite,images,maxFetch,perEmailLimit):
        '''
        This function processes the image locations, building the actual files and calling for email
        '''
        overallCount = 1
        attachmentList = []
        emailCount = 0
        for image in images:
            if overallCount <= maxFetch or maxFetch == -1:
                imageLocation = ImageFetcher.tidyUpFileLocationForSite(image,sourceSite)
                picture = ImageFetcher.fetchFile(imageLocation)
                if picture:
                    name = 'image'+str(overallCount)+ImageFetcher.getExtension(image)
                    pictureAndName = (name,picture)
                    attachmentList.append(pictureAndName)
                    overallCount += 1
                    emailCount += 1
                    if emailCount == perEmailLimit:
                        ResultsPage.sendMail(self,attachmentList)
                        attachmentList = []
                        emailCount = 0
        
    def sendMail(self,attachmentList):
        '''
        This function sends the email to the current user, with the specified attachment files.
        '''
        user = users.get_current_user()
        mail.send_mail(sender='colby.natale@gmail.com',
                  to=user.email(),
                  subject='Your fetched images',
                  body=user.nickname()+', please see your attached images from your recent fetch.',attachments=attachmentList)
              
application = webapp.WSGIApplication([('/', StartPage),('/results', ResultsPage)],debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()