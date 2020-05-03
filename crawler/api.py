import flask
from crawler import order
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/order', methods=['POST'])
def home():
    #try: 
        return order()
    #except: 
     #   return home()

app.run()
