import numpy as np
import math
import time
import pandas_datareader.data as web
from pandas_datareader._utils import RemoteDataError
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from flask import Flask, render_template,request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from flask_login import login_user, UserMixin, logout_user,LoginManager, current_user, login_required
from forms import SignupForm,LoginForm


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
@login_manager.user_loader
def load_user(user_id):
    return user.query.get(int(user_id))
class user(db.Model, UserMixin):

    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    stocks = db.relationship('stocks',backref='user',lazy=True)

class stocks(db.Model):

    __tablename__='stocks'
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(10),unique=True,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)



@app.route('/')
def home():
    return render_template('home.html')

@app.route("/dashboard", methods=['GET','POST'])
@login_required
def dashboard():
    if request.method=='POST':
        stock = request.form['stock'].upper()
        try:
            predict(stock)
        except RemoteDataError:
            flash('You have entered an incorrect stock name!', 'dark')
        time.sleep(10)
        return redirect(url_for('dashboard'))

    return render_template('base.html')


@app.route("/login" ,methods = ['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        User = user.query.filter_by(email = form.email.data).first()
        if User and sha256_crypt.verify(form.password.data,User.password):
            login_user(User)
            return redirect(url_for('dashboard'))
        flash('You have entered an incorrect email/password!', 'dark')
    return render_template("login.html")

@app.route("/signup", methods = ['GET','POST'])
def signup():
    form = SignupForm(request.form)
    if request.method =='POST' and form.validate():
        encPass=sha256_crypt.encrypt(str(form.password.data))
        User = user(username=form.username.data, email = form.email.data,password=encPass)
        db.session.add(User)
        db.session.commit()
        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)

#Linear regression function to generate prediction
def predict(stock):
    df = web.DataReader(stock, 'yahoo')
    #Use 1% of data length as the label and the rest as features
    predict = int(math.ceil(0.01*len(df)))

    df['Datez'] = df.index
    df = df[['Adj Close']]
    df['Prediction'] = df['Adj Close'].shift(-predict)
    #print(df)
    #Creating datasets
    #x-axis dataset

    x = np.array(df.drop(['Prediction'],1))
    x = preprocessing.scale(x)
    x_forecast = x[-predict:]
    x = x[:-predict]

    #y-axis dataset
    y = np.array(df['Prediction'])
    y = y[:-predict]
    #print(y)

    #Split datasets into 70% training and 30% testing
    x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.3)

    #Create linear regression model

    lr=LinearRegression(n_jobs=-1)
    lr.fit(x_train,y_train)

    lr_confidence = lr.score(x_test, y_test)
    #print(lr_confidence)

    #Set the new predicted values equal to last 30 rows of original df


    lr_prediction = lr.predict(x_forecast)
    #print(lr_prediction)

    x = [i for i in range(-predict,0)]
    #print(np.array(df[['Adj Close']]))
    plt.plot(x,np.array(df[['Adj Close']][-predict:]), label = "Prices of past {} days".format(predict))
    x = [i for i in range(0, predict)]
    plt.plot(x,lr_prediction, label="Predicted prices of next {} days".format(predict))
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend(loc=4)
    plt.title('Stock forecast for {}'.format(stock))
    plt.savefig('static/stock_analysis.jpg')


if __name__ == "__main__":

    app.secret_key = 'NQGXguWl9kkfpA4'
    app.run(debug=True, threaded=True)


