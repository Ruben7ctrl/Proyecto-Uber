from api.models import db, Driver, User, Vehicle
from werkzeug.security import generate_password_hash


def create_driver(data):
    # Validar email único
    if User.query.filter_by(email=data['email']).first():
        return None, {"email": ["Email already exists"]}

    vehicle = Vehicle.query.get(data['vehicle_id'])
    if not vehicle:
        return None, {"vehicle_id": ["Vehicle not found"]}

    driver = Driver(
        name=data['name'],
        email=data['email'],
        password=generate_password_hash(data['password']),
        role="driver",
        type="driver",
        vehicle=vehicle,
        profile_photo_path=data.get('profile_photo_path')
    )
    db.session.add(driver)
    db.session.commit()
    return driver, None


def update_driver(driver, data):
    if "name" in data:
        driver.name = data['name']
    if "email" in data:
        # Validar si cambia email y no existe duplicado
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != driver.id:
            return {"email": ["Email already exists"]}
        driver.email = data['email']
    if "password" in data:
        driver.password = generate_password_hash(data['password'])
    if "vehicle_id" in data:
        vehicle = Vehicle.query.get(data['vehicle_id'])
        if not vehicle:
            return {"vehicle_id": ["Vehicle not found"]}
        driver.vehicle = vehicle
    if "profile_photo_path" in data:
        driver.profile_photo_path = data['profile_photo_path']

    db.session.commit()
    return None


def delete_driver(driver):
    db.session.delete(driver)
    db.session.commit()
