from memeServer import app as application
application.config['DEBUG'] = True

if __name__ == "__main__":
    application.run(host = "0.0.0.0", port = 8080, debug=True)
