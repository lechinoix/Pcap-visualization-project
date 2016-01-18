# simple python server to serve html/javascript and restful service
import web
from Import import options

urls = ( "/service/stats", "stats" )

class stats:
    def GET(self):
        return open("data.json",'r').read()

if __name__ == "__main__":
    
    app = web.application(urls, globals())
    app.run() 

