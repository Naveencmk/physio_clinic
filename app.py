from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Use environment variable for database URL (Render will provide this)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- Models --------------------

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    treated = db.Column(db.Boolean, default=False)

class TreatedPatient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    treated_at = db.Column(db.DateTime, default=db.func.now())

# -------------------- Routes --------------------

@app.route('/api/send-message', methods=['POST'])
def receive_message():
    data = request.get_json()
    if not all(k in data for k in ('name', 'phone', 'email', 'service')):
        return jsonify({"error": "Missing required fields"}), 400

    new_apt = Appointment(
        name=data['name'],
        phone=data['phone'],
        email=data['email'],
        service=data['service'],
        message=data.get('message', '')
    )
    db.session.add(new_apt)
    db.session.commit()
    return jsonify({"status": "Message stored", "id": new_apt.id})

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.order_by(Appointment.id.desc()).all()
    return jsonify([{
        "id": apt.id,
        "name": apt.name,
        "phone": apt.phone,
        "email": apt.email,
        "service": apt.service,
        "message": apt.message,
        "treated": apt.treated
    } for apt in appointments])

@app.route('/api/treated-patients', methods=['POST'])
def mark_patient_treated():
    data = request.get_json()
    if not all(k in data for k in ('id', 'name', 'phone', 'email', 'service')):
        return jsonify({"error": "Missing required fields"}), 400

    treated = TreatedPatient(
        name=data['name'],
        phone=data['phone'],
        email=data['email'],
        service=data['service'],
        message=data.get('message', '')
    )
    db.session.add(treated)

    appointment = Appointment.query.get(data['id'])
    if appointment:
        appointment.treated = True

    db.session.commit()
    return jsonify({"status": "Treated patient stored", "id": treated.id})

@app.route('/api/treated-patients', methods=['GET'])
def get_treated_patients():
    patients = TreatedPatient.query.order_by(TreatedPatient.treated_at.desc()).all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "phone": p.phone,
        "email": p.email,
        "service": p.service,
        "message": p.message,
        "treated_at": p.treated_at.isoformat()
    } for p in patients])
@app.route('/api/admin/delete-all', methods=['GET', 'POST'])
def delete_all_data():
    # db.session.query(Appointment).delete()
    db.session.query(TreatedPatient).delete()
    db.session.commit()
    return jsonify({"status": "All data deleted"})
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    print("Received:", data)
    admin_id = data.get('adminId', '').strip()
    password = data.get('password', '').strip()

    # Exact match check
    if admin_id == 'ramya21' and password == '2003':
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401


# -------------------- App Entry --------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
