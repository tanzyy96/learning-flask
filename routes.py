from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User, Place
from forms import SignupForm, LoginForm, AddressForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/learningflask'
db.init_app(app)

app.secret_key = "development-key"

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/signup", methods=['GET', 'POST'])	# GET for going to the page ; POST for signup
def signup():
	form = SignupForm()

	if 'email' in session:
		redirect(url_for('home'))		# protection: if user is already logged in, send straight to home page

	if request.method =='POST':			# if signup 
		if form.validate() == False:	# validation fail -> refresh page
			return render_template('signup.html', form=form)
		else:
			newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)	# create new user; create new session
			db.session.add(newuser)
			db.session.commit()

			session['email'] = newuser.email
			return redirect(url_for('home'))

	elif request.method == 'GET':
		return render_template("signup.html", form=form)

@app.route("/login", methods = ['GET','POST'])	# GET for going to the page ; POST for sign-in
def login():
	form = LoginForm()

	if 'email' in session:
		redirect(url_for('home'))		# protection: if user is already logged in, send straight to home page

	if request.method == "POST":
		if form.validate() == False:	# validation fail -> refresh page
			return render_template("login.html", form=form)
		else:
			email = form.email.data
			password = form.password.data

			user = User.query.filter_by(email=email).first()	# check if user credentials exist

			if user is not None and user.check_password(password):
				session['email'] = form.email.data
				return redirect(url_for('home'))
			else:
				return redirect(url_for('login'))

	elif request.method == "GET":
		return render_template('login.html', form=form)

@app.route("/home", methods = ['GET', 'POST'])	# GET for going to the page ; POST for entering data
def home():
	if 'email' not in session:
		return redirect(url_for('login'))		# protection: if user login not confirmed, send to login page

	form = AddressForm()

	places = []
	my_coordinates = (37.4221, -122.0844)

	if request.method == 'POST':
		if form.validate() == False:
			return render_template('home.html', form=form)
		else:
			# get the address
			address = form.address.data

			# query for places around it
			p = Place()
			my_coordinates = p.address_to_latlng(address)
			places = p.query(address)

			# return those results
			return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)
			
	elif request.method == 'GET':
		return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places)

@app.route("/logout")
def logout():
	session.pop('email', None)					# end session:  pagereturn to index
	return redirect(url_for('index'))



if __name__ == "__main__":
	app.run(debug=True)

#source venv/bin/activate
#python routes.py