# Medscape Project Setup

This guide will help you set up and run the Medscape project on a Windows machine.

## 🚀 Getting Started

### **1️⃣ Clone the Repository**

Open a terminal and run the following command:

```sh
git clone git@github.com:zacmuturi45/sanyoo.git
cd your-project-folder
```

### **2️⃣ Backend Setup (Flask GraphQL)**

Navigate to the `backend` folder:

```sh
cd backend
```

#### **Create a Virtual Environment**
```sh
python -m venv venv
venv\Scripts\activate  # Windows activation
```

#### **Install Dependencies**
```sh
pip install -r requirements.txt
```

#### **Set Up Environment Variables**
Create a `.env` file in the `backend` directory and add your environment variables (e.g., database URL, secret keys).

#### **Run Database Migrations**
```sh
flask db upgrade
```

#### **Start the Backend Server**
```sh
flask run
```

---

### **3️⃣ Frontend Setup (Next.js + Apollo Client)**

Navigate to the `frontend` folder:

```sh
cd frontend
```

#### **Install Dependencies**
```sh
npm install
```

#### **Set Up Environment Variables**
Create a `.env.local` file in the `frontend` directory and configure the necessary API URLs.

#### **Run the Frontend Server**
```sh
npm run dev
```

---

## 🎯 Final Steps

Once both the frontend and backend are running, open your browser and visit:
```
http://localhost:3000
```
Your niece should now be able to use the full project on her Windows machine! 🚀

