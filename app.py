#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist {self.id} name: {self.name}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
      return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data=[]

  geos = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)

  for geo in geos:
      venues = db.session.query(Venue.id, Venue.name).filter(Venue.city == geo[0]).filter(Venue.state == geo[1])
      data.append({
        "city": geo.city,
        "state": geo.state,
        "venues": venues
      })
  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    
  search_term = request.form.get('search_term')
  data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%'))

  result = {
    "count": data.count(),
    "data": data,
  }
  return render_template('pages/search_venues.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()

  for show in shows:
    data = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
           "artist_image_link": show.artist.image_link,
           "start_time": format_datetime(str(show.start_time))
        }

    past_shows = []
    upcoming_shows = []
    if show.start_time > datetime.now():
      upcoming_shows.append(data)
    else:
      past_shows.append(data)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

    form = VenueForm()
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                  phone=form.phone.data, image_link=form.image_link.data,genres=form.genres.data,
                  facebook_link=form.facebook_link.data)
    try:
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue {venue_id} was successfully deleted.!')
  except Exception as e:
    error = True
    flash('An error occurred. Venue {venue_id} could not be deleted.!')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=[]
  artists = db.session.query(Artist.id, Artist.name)

  for artist in artists:
      data.append({
        "id": artist.id,
        "name": artist.name
      })

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

  result={
    "count": data.count(),
    "data": data
  }

  return render_template('pages/search_artists.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()

  for show in shows:
    data = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": format_datetime(str(show.start_time))
        }
    past_shows = []
    upcoming_shows = []
    if show.start_time > datetime.now():
      upcoming_shows.append(data)
    else:
      past_shows.append(data)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

 obj = Artist.query.filter_by(id=artist_id).first()
 artist = {
 "id": obj.id,
 "name": obj.name,
 "genres": obj.genres,
 "city": obj.city,
 "state": obj.state,
 "phone": obj.phone,
 "website": obj.website,
 "facebook_link": obj.facebook_link,
 "seeking_venue": obj.seeking_venue,
 "seeking_description": obj.seeking_description,
 "image_link": obj.image_link }

 artist = Artist.query.get(artist_id)
 form = ArtistForm(obj=artist)

 return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

    form = ArtistForm(request.form)
    artist = db.session.query(Artist).filter(Artist.id == artist_id).one()

    artist.name = request.form['name'],
    artist.city = request.form['city'],
    artist.state = request.form['state'],
    artist.address = request.form['address'],
    artist.phone = request.form['phone']

    try:
        db.session.add(artist)
        db.session.commit()
        flash('Artist' + form.name.data + ' was successfully updated!')
    except:
        flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  obj = Venue.query.filter_by(id=venue_id).first()
  venue = {
    "id": obj.id,
    "name": obj.name,
    "genres": obj.genres,
    "address": obj.address,
    "city": obj.city,
    "state": obj.state,
    "phone": obj.phone,
    "website": obj.website,
    "facebook_link": obj.facebook_link,
    "seeking_talent": obj.seeking_talent,
    "seeking_description": obj.seeking_description,
    "image_link": obj.image_link
  }
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    form = VenueForm(request.form)
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()

    venue.name = request.form['name'],
    venue.city = request.form['city'],
    venue.state = request.form['state'],
    venue.address = request.form['address'],
    venue.phone = request.form['phone']

    try:
        db.session.add(venue)
        db.session.commit()
        flash('Venue' + form.name.data + ' was successfully updated!')
    except:
        flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():

  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

    form =ArtistForm()
    artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data,
                  phone=form.phone.data, genres=form.genres.data,
                  facebook_link=form.facebook_link.data)
    try:
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/shows')
def shows():

    data = []
    shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()

    for show in shows:
        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show[0]).one()
        venue = db.session.query(Venue.name).filter(Venue.id == show[1]).one()

        data.append({
            "venue_id": show[1],
            "venue_name": venue[0],
            "artist_id": show[0],
            "artist_name": artist[0],
            "artist_image_link": artist[1],
            "start_time": str(show[2])
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():

  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False
  date_format = '%Y-%m-%d %H:%M:%S'

  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time = datetime.strptime(request.form['start_time'], date_format)
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    error = True
    print(f'Error ==> {e}')
    db.session.rollback()
  finally:
    db.session.close()
    if error: flash('An error occurred. Show could not be listed.')
    else: flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):

    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):

    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
