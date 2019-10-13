import os
import json
import glob
from uuid import uuid4
import tkinter as tk
from tkinter import filedialog
from flask import Flask, render_template,request, jsonify,send_file, redirect, url_for
from flask_restful import Resource, Api
import subprocess

application = Flask(__name__)
api =Api(application)
application.config['SECRET_KEY'] ='decf5b3e1ef04cc1185581d3f07c2af'

index= """
<div>
<form id="upload-form" action="/upload" method="POST" enctype="multipart/form-data">
    <strong>Files:</strong><br>
    Select files OR drag them into the box below.
    <input id="file-picker" type="file" name="file" accept="*" multiple><p>

    <div id="dropbox">
        Drag and Drop Files Here
    </div><p>

    <fieldset id="progress" style="display: none">
        <legend>Files Progress</legend>

        <div class="progress-trough">
            <div id="progress-bar" class="progress-bar">0%</div>
        </div>
    </fieldset><p>

    <input type="submit" value="Upload!" id="upload-button">
</form>
</div>
<script type="text/javascript" src="{{ url_for('static', filename='js/jquery-2.1.1.min.js') }}"></script>
<script type="text/javascript" src="{{ url_for('static', filename='js/uploadr.js') }}"></script>
"""


global fileslist
fileslist = []

@application.route('/success', methods = ['POST'])  
def success():  
    if request.method == 'POST':  
        f = request.files['file']  
        f.save(f.filename)  
        return render_template("success.html", name = f.filename)


@application.route("/sendfile", methods = ['POST'])
def sendfile():
    data = request.form.to_dict(flat=False)
    print(data["filename"][0])
    return send_file(data["filename"][0], as_attachment=True)


@application.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "static/uploads"
    if not os.path.isdir(target):
        try:
            os.mkdir(target)
        except:
            if is_ajax:
                return ajax_response(False, "Couldn't create upload directory: {}".format(target))
            else:
                return "Couldn't create upload directory: {}".format(target)

    print("=== Form Data ===")
    for key, value in list(form.items()):
        print(key, "=>", value)

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key))


@application.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "static/uploads/"
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    return render_template("success.html")


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))

@application.route("/")
def home():
    f = open("templates/tempcopy.html","w")
    string =""
    link="""<!DOCTYPE html>
    <html>
    <head>
        <style>
    .linkButton { 
         background: none;
         border: none;
         color: #0066ff;
         text-decoration: underline;
         cursor: pointer; 
    }
    </style>
    </head>
    <body>"""
    for i in fileslist:
        tmp = i[::-1].index("/")
        tmp = i[::-1][0:tmp][::-1]
        link = link + """
        <div>
        <form action="/sendfile"  method="post">
          <input  type="hidden" name="filename" value=\""""+i+"""\">
        <input type="submit" class="linkButton" value=\""""+tmp+"""\"/>
        </form> 
        </div>
        """

    # file upload form    
    link = link +index
    
    
    f.write(link)
    f.close()
    
    return render_template('tempcopy.html')

if __name__ == '__main__':
    root = tk.Tk()
    fileslist = []
    filez = filedialog.askopenfilenames(initialdir = os.path.join(os.environ["HOMEPATH"], "Desktop"),title = "Select file to transfer")
    fileslist = fileslist + list(root.tk.splitlist(filez))

    while(True):
        print(fileslist)
        root.destroy()
        s= input("Want to add more files: ")
        if (s.lower() =="y"):
            root = tk.Tk()
            filez = filedialog.askopenfilenames(initialdir = os.path.join(os.environ["HOMEPATH"], "Desktop"),title = "Select file to transfer")
            fileslist = fileslist + list(root.tk.splitlist(filez))
            continue
        else:
            break

    if not os.path.isdir("templates"):
        os.mkdir("templates")
    f = open("templates/tempcopy.html","w")
    f.close()
    
    # Python Program to Get IP Address
    process = subprocess.Popen("ipconfig", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.communicate()[0].decode("utf-8") 
    ind = output.index("Wireless LAN adapter Local Area Connection* 1:")
    ind = output.index("IPv4",ind)
    ind = output.index(": ",ind)
    ind2 =output.index("\r",ind)
    address= output[ind+2:ind2]
    import socket 
    hostname = socket.gethostname() 
    IPAddr = socket.gethostbyname(hostname) 
    print("Your Computer Name is:" + hostname) 
    print("\nPlease connect to:\n========================================\n"+ IPAddr+":80 OR "+address+":80\n========================================\n") 

    application.run(host='0.0.0.0',port=80)
  
