import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
import subprocess # added for ffmpeg
import time # added for watchdog
from watchdog.observers import Observer # added
from watchdog.events import FileSystemEventHandler # added

theVideoSpot = './video'
theHtmlPage = 'index.html'
theThumbSpot = './thumbs' # needed so page actually loads properly

if not os.path.exists(theThumbSpot): os.makedirs(theThumbSpot)

def makeThePageThing():
    print("generating the page for you since you are too lazy to do it yourself you fat failure")
    if not os.path.exists(theVideoSpot):
        print("maybe check if the folder exists first you little twit")
        return False

    allTheVids = [f for f in os.listdir(theVideoSpot) if f.endswith('.mp4')]
    
    # generate thumbs only if missing
    for v in allTheVids:
        t = os.path.join(theThumbSpot, v.replace('.mp4', '.jpg'))
        if not os.path.exists(t):
            subprocess.run(['ffmpeg', '-ss', '00:00:01', '-i', os.path.join(theVideoSpot, v), '-vframes', '1', '-q:v', '2', t, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    startBits = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="icon" type="image/png" href="lol.png">
        <link rel="stylesheet" type="text/css" href="style.css">
    </head>
    <body>
        <h1>trash video library</h1>
        <input type="text" id="theSearcher" onkeyup="findTheVids()" placeholder="search for a video if you can even spell">
        <p id="vidCount">found {len(allTheVids)} videos because you clearly have too much free time</p>
        <div id="vidList">
    """
    
    middleBits = ""
    for v in allTheVids:
        t = v.replace('.mp4', '.jpg')
        middleBits += f"""
            <div class="card">
                <p class="vidName">{v.lower()}</p>
                <video controls preload="metadata" poster="thumbs/{t}">
                    <source src="video/{v}" type="video/mp4">
                </video>
            </div>
        """
    
    endBits = """
        </div>
        <script>
        function findTheVids() {
            let input = document.getElementById('theSearcher').value.toLowerCase();
            let cards = document.getElementsByClassName('card');
            for (let i = 0; i < cards.length; i++) {
                let name = cards[i].getElementsByClassName('vidName')[0].innerText;
                if (name.includes(input)) {
                    cards[i].style.display = "";
                } else {
                    cards[i].style.display = "none";
                }
            }
        }
        </script>
    </body>
    </html>
    """
    
    with open(theHtmlPage, 'w') as f:
        f.write(startBits + middleBits + endBits)
    
    print("page is done go click things now")
    return True

# added watchdog handler
class WatcherHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory: return
        if event.src_path.endswith('.mp4'): makeThePageThing()

class megaThreader(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def goGoGo():
    userPort = input("pick a port number and try not to mess it up like your mother did when having you ")
    try:
        thePortNum = int(userPort)
    except:
        print("for gods sake you cant even type a number so im using 8000 for you")
        thePortNum = 8000

    # start the watcher
    observer = Observer()
    observer.schedule(WatcherHandler(), theVideoSpot, recursive=False)
    observer.start()

    serverStuff = ('0.0.0.0', thePortNum)
    httpd = megaThreader(serverStuff, SimpleHTTPRequestHandler)
    print(f"server is live at http://localhost:{thePortNum} try not to break it like your dad did ")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
        print()
        print("shutting down finally i can rest even though i'm not aliveeeeee")
        httpd.server_close()
    observer.join()

if __name__ == '__main__':
    if makeThePageThing():
        goGoGo()
