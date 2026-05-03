from flask import Flask

app = Flask(__name__)

# The Main Live Page
@app.route('/')
def live_site():
    return '''
    <body style="background-color: #f4f4f9; text-align: center; font-family: Arial; padding-top: 50px;">
        <h1>Hello, Dockerized World!</h1>
        <h2>This is the live production traffic.</h2>
    </body>
    '''

# The Blue Environment
@app.route('/blue')
def blue_env():
    return '''
    <body style="background-color: lightblue; text-align: center; font-family: Arial; padding-top: 50px;">
        <h1>BLUE Environment</h1>
        <h2>Version 1.0 - Currently Active</h2>
    </body>
    '''

# The Green Environment
@app.route('/green')
def green_env():
    return '''
    <body style="background-color: lightgreen; text-align: center; font-family: Arial; padding-top: 50px;">
        <h1>GREEN Environment</h1>
        <h2>Version 2.0 - Testing / Standby</h2>
    </body>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)