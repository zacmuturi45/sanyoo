from graphene import (
    Field,
    Int,
    List,
    String,
    relay,
    Schema,
    ObjectType,
    InputObjectType,
    Mutation,
    Boolean,
    ID,
    Union,
)

from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from sqlalchemy import func, or_, and_
from .models import (
    Patient as PatientModel,
    Doctor as DoctorModel,
    Assessment as AssessmentModel,
    Prescription as PrescriptionModel,
    Inventory as InventoryModel,
    db
)

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required

class Patient(SQLAlchemyObjectType):
    patient_id = Field(Int)

    class Meta:
        model = PatientModel
        interfaces = (relay.Node,)
    
    def resolve_patient_id(self, info):
        return self.id

class Doctor(SQLAlchemyObjectType):
    doctor_id = Field(Int)

    class Meta:
        model = DoctorModel
        interfaces = (relay.Node,)
    
    def resolve_doctor_id(self, info):
        return self.id

class Assessment(SQLAlchemyObjectType):
    assessment_id = Field(Int)

    class Meta:
        model = AssessmentModel
        interfaces = (relay.Node,)
    
    def resolve_assessment_id(self, info):
        return self.id

class Prescription(SQLAlchemyObjectType):
    prescription_id = Field(Int)

    class Meta:
        model = PrescriptionModel
        interfaces = (relay.Node,)
    
    def resolve_prescription_id(self, info):
        return self.id

class Inventory(SQLAlchemyObjectType):
    inventory_id = Field(Int)

    class Meta:
        model = InventoryModel
        interfaces = (relay.Node,)
    
    def resolve_inventory_id(self, info):
        return self.id
    

class CreatePatient(Mutation):
    class Arguments:
        full_name = String(required=True)
        age = Int(required=True)
        gender = String(required=True)
        phone = String(required=True)
        address = String(required=True)
    
    patient = Field(Patient)
    
    def mutate(self, info, full_name, age, gender, phone, address):
        patient = PatientModel(full_name=full_name, age=age, gender=gender, phone=phone, address=address)
        db.session.add(patient)
        db.session.commit()
        return CreatePatient(patient=patient)

class CreateDoctor(Mutation):
    class Arguments:
        full_name = String(required=True)
        specialty = String(required=True)
        phone = String(required=True)
        email = String(required=True)
    
    doctor = Field(Doctor)
    
    def mutate(self, info, full_name, specialty, phone, email):
        doctor = DoctorModel(full_name=full_name, specialty=specialty, phone=phone, email=email)
        db.session.add(doctor)
        db.session.commit()
        return CreateDoctor(doctor=doctor)
    
from datetime import datetime

class SignUpMutation(Mutation):
    class Arguments:
        full_name = String(required=True)
        age = Int(required=True)
        gender = String(required=True)
        phone = String(required=True)
        address = String()
        password = String(required=True)

    ok = Boolean()
    patient_id = ID()
    success_message = String()

    def mutate(self, info, full_name, age, gender, phone, address=None, password=None):
        # Check if phone or email already exists
        existing_patient = PatientModel.query.filter(
            (PatientModel.phone == phone) | (PatientModel.phone == phone)
        ).first()

        if existing_patient:
            raise Exception("A patient with this email or phone number already exists.")

        # Hash the password
        hashed_password = password

        # Create a new patient
        new_patient = PatientModel(
            full_name=full_name,
            age=age,
            gender=gender,
            phone=phone,
            address=address,
            date_registered=datetime.now(),
            password_hash=hashed_password
        )

        db.session.add(new_patient)
        db.session.commit()

        return SignUpMutation(
            ok=True,
            patient_id=new_patient.id,
            success_message="Patient registration successful."
        )

    
class LoginMutation(Mutation):
    class Arguments:
        full_name = String(required=True)
        password = String(required=True)

    ok = Boolean()
    token = String()
    user_id = ID()
    full_name = String()
    user_type = String()

    def mutate(self, info, full_name, password):
        user = PatientModel.query.filter_by(full_name=full_name).first()
        user_type = "Patient"

        if not user:
            user = DoctorModel.query.filter_by(full_name=full_name).first()
            user_type = "Doctor"

        if user and user.password_hash == password:
            token = create_access_token(identity=user.id)
            return LoginMutation(
                ok=True, token=token, user_id=user.id, full_name=user.full_name, user_type=user_type
            )
        if not user:
            raise Exception("User with the provided full name does not exist")
        if not check_password_hash(user.password_hash, password):
            raise Exception("Wrong Password")

        return LoginMutation(ok=False, token=None, user_id=None, full_name=None, user_type=None)

class CreatePatientAssessmentWithPrescription(Mutation):
    class Arguments:
        full_name = String(required=True)
        age = Int(required=True)
        gender = String(required=True)
        phone = String(required=True)
        address = String(required=True)
        password_hash = String(required=True)
        doctor_id = ID(required=True)
        symptoms = String(required=True)
        diagnosis = String(required=True)
        medication = String(required=True)
        dosage = String(required=True)
        instructions = String(required=True)

    patient = Field(lambda: Patient)
    assessment = Field(lambda: Assessment)
    prescription = Field(lambda: Prescription)

    def mutate(self, info, full_name, age, gender, phone, address, password_hash, doctor_id, symptoms, diagnosis, medication, dosage, instructions):
        # Ensure the doctor exists
        doctor = DoctorModel.query.get(doctor_id)
        if not doctor:
            raise Exception("Doctor not found.")

        # Create new patient
        new_patient = PatientModel(full_name=full_name, age=age, gender=gender, phone=phone, address=address, password_hash=password_hash)
        db.session.add(new_patient)
        db.session.commit()  # Save to get the patient ID

        # Create new assessment
        new_assessment = AssessmentModel(
            patient_id=new_patient.id,
            doctor_id=doctor_id,
            symptoms=symptoms,
            diagnosis=diagnosis,
        )
        db.session.add(new_assessment)
        db.session.commit()  # Save to get the assessment ID

        # Create new prescription linked to the assessment
        new_prescription = PrescriptionModel(
            patient_id=new_patient.id,
            assessment_id=new_assessment.id,
            medication=medication,
            dosage=dosage,
            instructions=instructions
        )
        db.session.add(new_prescription)
        db.session.commit()

        return CreatePatientAssessmentWithPrescription(
            patient=new_patient,
            assessment=new_assessment,
            prescription=new_prescription
        )




class Query(ObjectType):
    all_patients = List(Patient)
    all_doctors = List(Doctor)
    all_assessments = List(Assessment)
    all_prescriptions = List(Prescription)
    all_inventory = List(Inventory)
    user_exists = String(full_name=String())
    doctor_assessments = List(Assessment, doctor_id=Int(required=True))
    patient_assessments = List(Assessment, full_name=String(required=True))

    def resolve_doctor_assessments(self, info, doctor_id):
        return AssessmentModel.query.filter_by(doctor_id=doctor_id).all()
    
    def resolve_patient_assessments(self, info, full_name):
        patient = PatientModel.query.filter_by(full_name=full_name).first()
        if patient:
            return patient.assessments

        return "User does not exist"
    
    def resolve_user_exists(self, info, full_name):
        doctor = DoctorModel.query.filter_by(full_name=full_name).first()
        if doctor:
            return "Doctor"

        patient = PatientModel.query.filter_by(full_name=full_name).first()
        if patient:
            return "Patient"

        return "User does not exist"
    
    def resolve_all_patients(self, info):
        return PatientModel.query.all()
    
    def resolve_all_doctors(self, info):
        return DoctorModel.query.all()
    
    def resolve_all_assessments(self, info):
        return AssessmentModel.query.all()
    
    def resolve_all_prescriptions(self, info):
        return PrescriptionModel.query.all()
    
    def resolve_all_inventory(self, info):
        return InventoryModel.query.all()

class Mutation(ObjectType):
    create_patient = SignUpMutation.Field()
    create_doctor = CreateDoctor.Field()
    login = LoginMutation.Field()
    create_patient_assessment_with_prescription = CreatePatientAssessmentWithPrescription.Field()



schema = Schema(query=Query, mutation=Mutation)
