from web_server.app import app
import logging

if __name__ == "__main__":
    logging.basicConfig(filename='LOGFILE', level=logging.DEBUG)
    app.run(debug=True)
