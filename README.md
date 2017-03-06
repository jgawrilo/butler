# butler

https://drive.google.com/open?id=0B7__u9BeTQu_UC1wYTk4YmhXMUE

clone the repo

To install chrome browser plugin...
1. Go to extensions.
2. Load upacked extension.
3. Select the chrome-extension directory

To run the socket server and run Butler...
1. Navigate to server directory
2. npm install
3. Go go http://localhost:3000/index2.html

To run the data server...
1. Nativate to contrib directory
2. pip install -r requirements.txt
3. python server2.py

This project is VERY buggy right now.  Follow the video script only to exercise the calls and see the data.

Please see server/public/mine.js.  The top of the file has the calls the user (ui) will make to the server such as clearing results, and unliking links, etc.  The bottom of the file has the socketio callbacks to hook into as data is processed and the user browses naturally.

server2.py has all of the details on what's happening but this is extremely beta at the moment and very sloppy.  Beware!
