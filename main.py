from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWsadmcasmdaclsdlldmlasladscavsdalcdal'
Bootstrap(app)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///shows-collection.db"
db.init_app(app)

search_result = []


# #CREATE TABLE
class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), unique=False, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), unique=False, nullable=False)
    img_url = db.Column(db.String(250), unique=False, nullable=False)


class UnwatchedShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), unique=False, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), unique=False, nullable=False)
    img_url = db.Column(db.String(250), unique=False, nullable=False)

    # Optional: this will allow each object to be identified by its title when printed.
    # def __repr__(self):
    #     return f'{self.title} - {self.author} - {self.rating}/10'


with app.app_context():
    db.create_all()

    # create wtform for movie editing


class ShowForm(FlaskForm):
    review = StringField('New review', validators=[DataRequired()])
    rating = StringField('rating 0-10 (9eg. 9.9)', validators=[DataRequired()])
    button = SubmitField('confirm change')


class NewShowForm(FlaskForm):
    title = StringField('type the title', validators=[DataRequired()])
    choice = RadioField('Have you watched or adding on watchlist?',
                        choices=[('watched', 'Watched'), ('watchlist', 'WatchList')])

    button = SubmitField('add')


# new_show = Show(
#     title="Dxd",
#     year=2012,
#     description="boobs, pussies and sex",
#     rating=99,
#     ranking=10,
#     review="It was a good movie",
#     img_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSqsYbqyub8mN2ViBP-"
#             "erLtmVC8s9YGBQaz_TNkkgskqbgpfDqCrYe_7sXRppv8iF0fMdc&usqp=CAU"
# )
# with app.app_context():
#     db.session.add(new_show)
#     db.session.commit()

@app.route("/")
def home():

    unwatched_shows = UnwatchedShow.query.order_by(UnwatchedShow.id).all()
    unwatched_shows_title = UnwatchedShow.query.order_by(UnwatchedShow.title).all()
    shows_title = Show.query.order_by(Show.title).all()
    shows = Show.query.order_by(Show.rating).all()
    for i in range(len(shows)):
        shows[i].ranking =  len(shows) - i
    shows = Show.query.order_by(Show.ranking).all()
    db.session.commit()

    for i in range(len(unwatched_shows_title)):
        for j in range(len(shows_title)):
            if shows_title[j].title == unwatched_shows_title[i].title:
                print(shows_title[j].title, unwatched_shows_title[i].title )
                selected_show = UnwatchedShow.query.get(unwatched_shows_title[i].id)
                db.session.delete(selected_show)
            db.session.commit()
    return render_template("index.html", shows=shows, unwatched_shows=unwatched_shows)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    show_id = request.args.get('id')
    print(show_id)
    selected_show = Show.query.get(show_id)
    form = ShowForm()
    if request.method == "POST":
        selected_show.review = request.form['review']
        selected_show.rating = request.form['rating']
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", show=selected_show, form=form)


@app.route("/add-from-watchlist", methods=['GET', 'POST'])
def add_from_watchlist():
    show_id = request.args.get('id_watch')
    print(show_id)
    selected_show = UnwatchedShow.query.get(show_id)
    form = ShowForm()
    if request.method == "POST":
        new_show = Show(
            title=selected_show.title,
            year=selected_show.year,
            description=selected_show.description,
            rating=request.form['rating'],
            ranking='0',
            img_url=selected_show.img_url,
            review=request.form['review'],
        )
        db.session.delete(selected_show)
        db.session.add(new_show)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", show=selected_show, form=form)


@app.route("/delete-from-watchlist")
def delete_from_watchlist():
    show_id = request.args.get('id_watch')
    selected_show = UnwatchedShow.query.get(show_id)
    db.session.delete(selected_show)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/delete")
def delete():
    show_id = request.args.get('id')
    selected_show = Show.query.get(show_id)
    db.session.delete(selected_show)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    global search_result
    form = NewShowForm()
    if request.method == 'POST':
        url = 'https://api.tvmaze.com/search/shows?'
        query = {
            'q': f"{request.form['title']}",
        }
        show_info = request.form['choice']
        response = requests.get(url=url, params=query)
        response.raise_for_status()
        search_result = response.json()
        return render_template('select.html', results=search_result, show_info=show_info)
    return render_template('add.html', form=form)


@app.route("/select", methods=['GET', 'POST'])
def select():
    global search_result
    show_info = str(request.args.get('show_info'))
    print(len(show_info))
    show_id = request.args.get('id_show')
    print(show_info)
    if show_info == 'watched':
        for target in search_result:
            if show_id == str(target['show']['id']):
                print(target['show']['name'])
                print(target['show']['premiered'].split('-')[0])
                print(target['show']['summary'].replace('<p>', '').replace('</p>', ''))
                print(target['show']['image']['original'])
                new_show = Show(
                    title=f"{target['show']['name']}",
                    year=target['show']['premiered'].split('-')[0],
                    description=target['show']['summary'].replace('<p>', '').replace('</p>', ''),
                    rating='0',
                    ranking='0',
                    img_url=target['show']['image']['original'],
                    review='',
                )
                with app.app_context():
                    db.session.add(new_show)
                    db.session.commit()

                show_id = Show.query.filter_by(title=f"{target['show']['name']}").first().id

                return redirect(url_for("edit", id=show_id))
    if show_info == 'watchlist':
        print('Welcome to watchlist')
        for target in search_result:
            if show_id == str(target['show']['id']):
                print(target['show']['name'])
                print(target['show']['premiered'].split('-')[0])
                print(target['show']['summary'].replace('<p>', '').replace('</p>', ''))
                print(target['show']['image']['original'])
                new_show = UnwatchedShow(
                    title=f"{target['show']['name']}",
                    year=target['show']['premiered'].split('-')[0],
                    description=target['show']['summary'].replace('<p>', '').replace('</p>', ''),
                    rating='0',
                    ranking='0',
                    img_url=target['show']['image']['original'],
                    review='',
                )
                with app.app_context():
                    db.session.add(new_show)
                    db.session.commit()

                return redirect(url_for("home"))
    return render_template('select.html')


if __name__ == '__main__':
    app.run(debug=True)
