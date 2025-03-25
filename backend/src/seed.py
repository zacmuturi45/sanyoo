from flask import Flask
from src import create_app
from src.models import db, Patient, Doctor, Assessment, Prescription, Inventory
from faker import Faker
import random


fake = Faker()

specialties = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General Medicine"]
medications = ["Paracetamol", "Ibuprofen", "Amoxicillin", "Metformin", "Aspirin"]

def create_fake_patient():
    return Patient(
        full_name=fake.name(),
        age=random.randint(1, 90),
        gender=random.choice(["Male", "Female"]),
        phone=fake.phone_number(),
        address=fake.address(),
        password_hash="sanyooo"
    )


def create_fake_doctor():
    return Doctor(
        full_name=fake.name(),
        specialty=random.choice(specialties),
        phone=fake.phone_number(),
        email=fake.email(),
        password_hash="sanyooo"
    )


def create_fake_assessment(patient_id, doctor_id):
    return Assessment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        symptoms=fake.sentence(),
        diagnosis=fake.sentence()
    )


def create_fake_prescription(patient_id, assessment_id):
    return Prescription(
        patient_id=patient_id,
        assessment_id=assessment_id,
        medication=random.choice(medications),
        dosage=f"{random.randint(1, 3)} pills per day",
        instructions=fake.sentence()
    )


def create_fake_inventory():
    return Inventory(
        drug_name=random.choice(medications),
        quantity=random.randint(10, 500),
        supplier=fake.company()
    )


def seed():
    db.session.query(Prescription).delete()
    db.session.query(Assessment).delete()
    db.session.query(Patient).delete()
    db.session.query(Doctor).delete()
    db.session.query(Inventory).delete()
    db.session.commit()

    patients = [create_fake_patient() for _ in range(10)]
    doctors = [create_fake_doctor() for _ in range(5)]
    inventories = [create_fake_inventory() for _ in range(5)]

    db.session.add_all(patients + doctors + inventories)
    db.session.commit()

    assessments = []
    prescriptions = []

    for patient in patients:
        doctor = random.choice(doctors)
        assessment = create_fake_assessment(patient.id, doctor.id)
        db.session.add(assessment)
        db.session.commit()
        
        prescription = create_fake_prescription(patient.id, assessment.id)
        prescriptions.append(prescription)

    db.session.add_all(prescriptions)
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed()
