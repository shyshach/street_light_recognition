import os
import time
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from forms import RegistrationForm, LoginForm
from flask import Flask, flash, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
from inference import load_model, get_result
from models import db, User, Record, City, Street, House, Role
import pymysql


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

UPLOAD_FOLDER = 'static/uploads/'


def create_app():
    application = Flask(__name__)
    application.secret_key = "secret key"
    application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/street_light'
    db.init_app(application)
    return application


app = create_app()

login_manager = LoginManager()
login_manager.init_app(app)

filename = ''
net, output_layers, classes = load_model()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        exist_user = User.query.filter_by(email=form.email.data).first()
        if exist_user:
            return redirect(url_for('login'))

        user = User(phone=form.phone.data, email=form.email.data, role=1)
        user.set_password(form.password1.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid email address or Password.')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main'))


@login_required
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    query_args = request.form
    house_id = query_args.get('house_id')
    original_photo = query_args.get('original_photo')
    processed_photo = query_args.get('processed_photo')
    quantity = query_args.get('quantity')

    if not house_id:
        return jsonify({'error': 'Select house number!'})

    new_record = Record(house_id=house_id, original_photo=original_photo, processed_photo=processed_photo,
                        quantity=quantity, timestamp=int(time.time()))
    db.session.add(new_record)
    db.session.commit()
    db.session.flush()

    timestamp = datetime.fromtimestamp(new_record.timestamp)
    house = House.query.filter_by(house_id=house_id).first()
    house_number = house.house_number
    street = Street.query.filter_by(street_id=house.street).first()
    city = City.query.filter_by(city_id=street.city).first()
    results = {
        'house_number': house_number,
        'street': street.street_name,
        'city': city.city_name,
        'timestamp': timestamp.strftime('%m/%d/%Y %H:%M:%S')
    }
    return jsonify(results)


@login_required
@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    query_args = request.form
    house_number = query_args.get('house_number')
    user = query_args.get('user')
    street = query_args.get('street')
    user_role = User.query.filter_by(id=user).first().role
    user_house = House.query.filter_by(owner=user)
    if user_role == 1 and user_house:
        return jsonify({'error': 'House admin can be owner only for 1 house!'}), 400
    new_house = House(owner=user, street=street, house_number=house_number)
    db.session.add(new_house)
    db.session.commit()
    return f"Done!!"


@login_required
@app.route('/add_street', methods=['GET', 'POST'])
def add_street():
    query_args = request.form
    user = query_args.get('user')
    street = query_args.get('street')
    city = query_args.get('city')
    user_role = User.query.filter_by(id=user).first().role
    user_street = Street.query.filter_by(owner=user)
    if user_role == 2 and user_street:
        return jsonify({'error': 'Street admin can be owner only for 1 street!!'}), 400
    new_street = Street(owner=user, street_name=street, city=city)
    db.session.add(new_street)
    db.session.commit()
    return f"Done!!"


@login_required
@app.route('/add_city', methods=['GET', 'POST'])
def add_city():
    query_args = request.form
    user = query_args.get('user')
    city = query_args.get('city')
    user_role = User.query.filter_by(id=user).first().role
    user_city = City.query.filter_by(owner=user).first()
    if user_role == 3 and user_city:
        return jsonify({'error': 'City admin can be owner only for 1 city!'}), 400
    new_city = City(owner=user, city_name=city)
    db.session.add(new_city)
    db.session.commit()
    return f"Done!!"


def update_user_roles(user_id, previous_owner):
    for user in user_id, previous_owner:
        user_street = Street.query.filter_by(owner=user).first()
        user_city = City.query.filter_by(owner=user).first()
        user_role = User.query.filter_by(id=user).first().role

        if user_role == 4:
            pass
        elif user_city:
            db.session.query(User).filter(User.id == user).update({'role': 3})
        elif user_street:
            db.session.query(User).filter(User.id == user).update({'role': 2})
        else:
            db.session.query(User).filter(User.id == user).update({'role': 1})

        db.session.commit()


@login_required
@app.route('/change_house', methods=['GET', 'POST'])
def change_house():
    query_args = request.form
    user_id = query_args.get('user_id')
    house_id = query_args.get('house_id')
    previous_owner = House.query.filter_by(house_id=house_id).first().owner
    user_role = User.query.filter_by(id=user_id).first().role
    user_house = House.query.filter_by(owner=user_id).first()

    if user_role == 1 and user_house:
        return jsonify({'error': 'House admin can be owner only for 1 house!'}), 400
    db.session.query(House).filter(House.house_id == house_id).update({'owner': user_id})
    db.session.commit()
    update_user_roles(user_id, previous_owner)
    return f"Done!!"


@login_required
@app.route('/change_street', methods=['GET', 'POST'])
def change_street():
    query_args = request.form
    user_id = query_args.get('user_id')
    street_id = query_args.get('street_id')
    previous_owner = Street.query.filter_by(street_id=street_id).first().owner
    user_role = User.query.filter_by(id=user_id).first().role
    user_street = Street.query.filter_by(owner=user_id).first()
    if user_role == 2 and user_street:
        return jsonify({'error': 'Street admin can be owner only for 1 street!'}), 400
    db.session.query(Street).filter(Street.street_id == street_id).update({'owner': user_id})
    db.session.commit()
    update_user_roles(user_id, previous_owner)
    return f"Done!!"


@login_required
@app.route('/change_city', methods=['GET', 'POST'])
def change_city():
    query_args = request.form
    user_id = query_args.get('user_id')
    city_id = query_args.get('city_id')
    previous_owner = City.query.filter_by(city_id=city_id).first().owner
    user_role = User.query.filter_by(id=user_id).first().role
    user_city = City.query.filter_by(owner=user_id).first()

    if user_role == 3 and user_city:
        return jsonify({'error': 'City admin can be owner only for 1 city!'}), 400
    db.session.query(City).filter(City.city_id == city_id).update({'owner': user_id})
    db.session.commit()
    update_user_roles(user_id, previous_owner)
    return f"Done!!"


@app.route('/get_houses', methods=['GET'])
def get_houses():
    query_args = request.args
    street_id = query_args.get('street_id')
    houses_of_street = [{'id': house.house_id, 'number': house.house_number, 'email': User.query.filter_by(
        id=house.owner).first().email} for house in House.query.filter_by(street=street_id).order_by(House.house_number)]
    return jsonify(houses_of_street)


@app.route('/get_streets', methods=['GET'])
def get_streets():
    query_args = request.args
    city_id = query_args.get('city')
    streets_of_city = [{'id': street.street_id, 'street_name': street.street_name}
                       for street in Street.query.filter_by(city=city_id)]
    return jsonify(streets_of_city)


@app.route('/admin')
def admin(filename='default_image.png'):
    try:
        user_id = current_user.id
    except AttributeError:
        return redirect(url_for('/'))

    if current_user.is_active:
        role = Role.query.filter_by(id=current_user.role).first().role
    else:
        role = ''

    template_name = ''
    template_settings = {
        'role': role,
        'house_dict': {},
        'houses_of_street': [],
        'street_dict': {},
        'city_dict': {},
        'streets_of_city': [],
        'houses_of_city': [],
        'rows': [],
        'cities': [],
        'filename': filename
    }

    all_users = set(item.id for item in User.query.all())
    users_with_houses = set(item.User.id for item in db.session.query(User, House).filter(User.id == House.owner).all())
    users_without_house = all_users - users_with_houses
    users_without_house_dict = [{'id': User.query.filter_by(id=item).first().id,
                                 'email': User.query.filter_by(id=item).first().email} for item in users_without_house]
    template_settings.update({'users_without_house_dict': users_without_house_dict, 'all_users': all_users})

    if current_user.role == 1:
        template_name = 'house_admin.html'
        house = House.query.filter_by(owner=user_id).first()
        if not house:
            return render_template('homeless.html')
        house_id = house.house_id
        house_dict = {'house_id': house_id, 'house_number': house.house_number}
        street_id = house.street
        street = Street.query.filter_by(street_id=street_id).first()
        street_dict = {'street_id': street.street_id, 'street_name': street.street_name}
        city = City.query.filter_by(city_id=street.city).first()
        city_dict = {'id': city.city_id, 'city_name': city.city_name}
        rows = Record.query.filter_by(house_id=house_id).order_by(Record.id.desc())
        template_settings.update({'house_dict': house_dict, 'street_dict': street_dict, 'city_dict': city_dict,
                                  'rows': rows})

    elif current_user.role == 2:
        template_name = 'street_admin.html'
        street = Street.query.filter_by(owner=user_id).first()
        street_dict = {'street_id': street.street_id, 'street_name': street.street_name}
        houses_of_street = [{'id': house.house_id, 'number': house.house_number,
                             'email': User.query.filter_by(id=house.owner).first().email} for house in
                            House.query.filter_by(street=street.street_id).order_by(House.house_number)]
        city = City.query.filter_by(city_id=street.city).first()
        city_dict = {'id': city.city_id, 'city_name': city.city_name}
        rows = [item[0] for item in db.session.query(Record, House).filter(
            Record.house_id == House.house_id).filter(House.street == street.street_id).order_by(
            Record.id.desc()).all()]
        template_settings.update({'houses_of_street': houses_of_street, 'street_dict': street_dict,
                                  'city_dict': city_dict, 'rows': rows})

    elif current_user.role == 3:
        template_name = 'city_admin.html'
        city = City.query.filter_by(owner=current_user.id).first()
        city_dict = {'id': city.city_id, 'city_name': city.city_name}
        streets_of_city = [{'street_id': street.street_id, 'street_name': street.street_name,
                            'street_user': User.query.filter_by(id=street.owner).first().email} for street
                           in Street.query.filter_by(city=city.city_id)]
        houses_of_city = []
        for street in streets_of_city:
            for house in House.query.filter_by(street=street['street_id']):
                houses_of_city.append({'street_id': street['street_id'], 'street_name': street['street_name'],
                                       'house_id': house.house_id, 'house_number': house.house_number,
                                       'house_owner': house.owner, 'owner_email': User.query.filter_by(
                        id=house.owner).first().email})

        all_users = [{'user_id': item, 'user_email': User.query.filter_by(id=item).first().email} for item in all_users]

        rows = [item[0] for item in db.session.query(Record, House, Street).filter(
            Record.house_id == House.house_id).filter(House.street == Street.street_id).filter(
            Street.city == city.city_id).order_by(Record.id.desc()).all()]
        template_settings.update({'city_dict': city_dict, 'streets_of_city': streets_of_city,
                                  'houses_of_city': houses_of_city, 'rows': rows, 'all_users': all_users})

    elif current_user.role == 4:
        template_name = 'super_admin.html'
        all_users = [{'user_id': item, 'user_email': User.query.filter_by(id=item).first().email} for item in all_users]
        cities = City.query.all()
        city_dict = [{'id': city.city_id, 'city_name': city.city_name} for city in cities]
        streets_of_city = [{'city': City.query.filter_by(city_id=street.city).first().city_name,  'street_id': street.street_id,
                            'street_name': street.street_name, 'street_user':
                                User.query.filter_by(id=street.owner).first().email} for street
                           in Street.query.order_by(Street.city.asc()).all()]
        houses_of_city = []
        for street in streets_of_city:
            for house in House.query.filter_by(street=street['street_id']):
                houses_of_city.append({'street_id': street['street_id'], 'street_name': street['street_name'],
                                       'house_id': house.house_id, 'house_number': house.house_number,
                                       'house_owner': house.owner, 'owner_email': User.query.filter_by(
                        id=house.owner).first().email})

        cities = [{'city_name': city.city_name, 'city_id': city.city_id, 'user_id': city.owner,
                   'user_email': User.query.filter_by(id=city.owner).first().email} for city in cities]
        rows = Record.query.order_by(Record.id.desc()).all()
        template_settings.update({'city_dict': city_dict, 'streets_of_city': streets_of_city, 'cities': cities,
                                  'houses_of_city': houses_of_city, 'rows': rows, 'all_users': all_users})

    else:
        flash('Wrong template')

    for record in template_settings['rows']:
        current_row = House.query.filter_by(house_id=record.house_id).first()
        record.house_number = current_row.house_number
        street = Street.query.filter_by(street_id=current_row.street).first()
        record.street = street.street_name
        record.city = City.query.filter_by(city_id=street.city).first().city_name
        time_format = datetime.fromtimestamp(record.timestamp)
        record.timestamp = time_format.strftime('%m/%d/%Y %H:%M:%S')

    return render_template(template_name, **template_settings)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/admin', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        global filename
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    else:
        flash('Allowed image types are -> png, jpg, jpeg')
        return jsonify({'error': 'Wrong image format!'})


@app.route('/display/<filename>')
def display_image(filename):
    print('display_image filename: ' + filename)
    return redirect(url_for('static', filename=filename), code=301)


@app.route('/get_prediction')
def get_prediction():
    imagePath = os.path.join(UPLOAD_FOLDER, filename)
    img, lum = get_result(imagePath, net, output_layers, classes)
    return jsonify({'original_img': imagePath, 'luminosity': lum, 'img': img})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
