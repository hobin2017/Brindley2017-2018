"""
returning json;
"""
from flask import Flask
app = Flask(__name__)

@app.route('/test1/')
def test1():
    return '''
    {
    "employees": [
    { "firstName":"Bill" , "lastName":"Gates" },
    { "firstName":"George" , "lastName":"Bush" },
    { "firstName":"Thomas" , "lastName":"Carter" }
    ]}'''


if __name__ == '__main__':
    app.run(debug=True)
