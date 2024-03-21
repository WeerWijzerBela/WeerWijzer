import webbrowser
import codecs

def index():
    # Hier kan je extra logica toevoegen voordat de webserver start, indien nodig
    #run(host='localhost', port=8000)
    file = codecs.open("index.html", 'r', "utf-8")

    print(file.read())
    # webbrowser.open("index.html")
