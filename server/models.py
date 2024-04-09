from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship("HeroPower", back_populates="hero", cascade='all, delete-orphan')

    serialize_rules = ('-hero_powers.hero', '-hero_powers.power',)
    
    powers = association_proxy('hero_powers', 'power',
                               creator=lambda power_obj: HeroPower(power = power_obj))
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'super_name': self.super_name,
        }

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship
    hero_powers = db.relationship("HeroPower", back_populates="power", cascade='all, delete-orphan')

    serialize_rules = ('-hero_powers.power', '-hero_powers.hero',)

    heroes = association_proxy('hero_powers', 'hero',
                               creator=lambda hero_obj: HeroPower(hero = hero_obj))

    @validates("description")
    def validates_description(self, key, description):
        if not description or len(description) <= 20:
            raise ValueError("Power must have a description and be 20 characters long")
        return description
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    # add relationships
    hero = db.relationship('Hero', back_populates="hero_powers")
    power = db.relationship('Power', back_populates="hero_powers")

    serialize_rules = ('-hero.hero_powers', '-power.hero_powers',)

    @validates("strength")
    def validates_strength(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be one of the specified values")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'


