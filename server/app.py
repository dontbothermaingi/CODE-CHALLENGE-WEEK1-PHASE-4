#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes]), 200


@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    session = db.session
    hero = session.get(Hero, id)

    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    return jsonify(hero.to_dict()), 200


@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers]), 200


@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def get_and_update_powers_by_id(id):
        
    session = db.session
    power = session.get(Power, id)

    if not power:
        return jsonify({'error': "Power not found"}), 404

    if request.method == 'GET':
        return jsonify(power.to_dict()), 200

    elif request.method == "PATCH":
        data = request.json

        if not data:
            return jsonify({'error': 'No data provided for update'}), 400

        # Validate the description attribute
        description = data.get('description')
        if description and len(description) < 20:
            return jsonify({'error': 'Description must be a string and at least 20 characters long'}), 400

        # Update allowed attributes
        allowed_attributes = ['name', 'description']
        for attr, value in data.items():
            if attr in allowed_attributes:
                setattr(power, attr, value)
            else:
                return jsonify({'error': 'Invalid attribute'}), 400

        db.session.commit()

        return jsonify(power.to_dict()), 200



@app.route('/hero_powers', methods=['GET', 'POST'])
def get_and_post_hero_powers():
    if request.method == 'GET':
        hero_powers = HeroPower.query.all()
        return jsonify([hero_power.to_dict() for hero_power in hero_powers]), 200

    elif request.method == "POST":
        data = request.json
        strength = data.get('strength')

        if strength not in ['Strong', 'Weak', 'Average']:
            return jsonify({'errors': ['Strength must be one of: "Strong", "Weak", "Average"']}), 400
    
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')

        new_hero_power = HeroPower(
            strength=strength,
            hero_id=hero_id,
            power_id=power_id
        )

        db.session.add(new_hero_power)
        db.session.commit()

        return jsonify(new_hero_power.to_dict()), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
