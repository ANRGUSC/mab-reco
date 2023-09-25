from flask import Flask, request, redirect, url_for, session
import main 

app = Flask(__name__)

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        print(user_id)
        return main.main(user_id)
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    user_id = request.args.get('user_id')
    session['user_id'] = user_id
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)