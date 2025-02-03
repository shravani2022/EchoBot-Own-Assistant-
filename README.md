# EchoBot-Own-Assistant

## 🚀 EchoSphere: AI-Powered Conversational Assistant 🎙️💬

EchoSphere is an intelligent and responsive chatbot assistant designed to enhance conversations with seamless interactions. It echoes user queries with insightful responses, creating a dynamic and engaging communication experience. Whether for personal assistance or business support, EchoSphere adapts to needs with efficiency and clarity.

---

## 🌟 Key Features

✅ **Speech-to-Text** – Converts voice input into text using Google’s Speech Recognition.

✅ **Text-to-Speech** – Generates AI-powered voice responses with customizable language preferences.

✅ **AI-Powered Chat** – Delivers context-aware responses via an AI model.

✅ **Secure & Personalized** – User authentication, chat history, and voice-enabled interactions.

✅ **Flask-Based Web App** – Built using Flask and SQLAlchemy for robust backend support.

✅ **Mistral Integration** – Uses Mistral’s API for intelligent and accurate conversational responses.

✅ **User Preferences** – Customize themes, voice responses, and language settings.

✅ **Favorites & Categories** – Organize and manage chats with favorites and categories.

---

## 🏗️ Tech Stack

- **Backend:** Flask, Flask-Login, SQLAlchemy
- **Database:** SQLite
- **AI & NLP:** Mistral API
- **Voice Processing:** gTTS, SpeechRecognition
- **Frontend:** HTML, CSS, JavaScript
- **Environment Variables:** dotenv

---

## 📂 Project Structure

```
shravani2022-echobot-own-assistant/
├── README.md
└── Voice_Assistant/
    ├── app.py               # Main Flask Application
    ├── requirements.txt     # Dependencies
    ├── static/
    │   ├── login.css
    │   ├── scripts.js
    │   └── styles.css
    └── templates/
        ├── index.html
        ├── login.html
        └── register.html
```

---

## 🔧 Installation & Setup

### 1️⃣ Prerequisites
- Python 3.7+
- Virtual Environment (recommended)

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/shravani2022/echobot-own-assistant.git
cd echobot-own-assistant/Voice_Assistant
```

### 3️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Set Up Environment Variables
Create a `.env` file in the **Voice_Assistant/** directory and add the following:
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///chat.db
MISTRAL_API_KEY=your-mistral-api-key
MISTRAL_API_URL=https://api.mistral.ai/v1/chat/completions
```

### 6️⃣ Initialize the Database
```bash
python -c "from app import db; db.create_all()"
```

### 7️⃣ Run the Application
```bash
python app.py
```
The app will be available at `http://127.0.0.1:5000/`.

---

## 🚀 Usage

### **1️⃣ Register/Login**
- Open the web app and create an account.
- Login to access chat features.

### **2️⃣ Start a Conversation**
- Type or speak your query to get responses.
- Save important chats or mark favorites.

### **3️⃣ Customize Settings**
- Set theme preferences (light/dark mode).
- Enable voice responses.
- Choose preferred AI model.

### **4️⃣ Manage Chats**
- View past conversations.
- Delete or organize chats into categories.

---

## 🛠️ API Endpoints

### **Authentication**
| Endpoint       | Method | Description        |
|---------------|--------|--------------------|
| `/register`   | POST   | User Registration  |
| `/login`      | POST   | User Login        |
| `/logout`     | GET    | User Logout       |

### **Chat Operations**
| Endpoint               | Method | Description                     |
|------------------------|--------|---------------------------------|
| `/api/chats`          | GET    | Get all user chats             |
| `/api/chat/<chat_id>` | GET    | Get details of a specific chat |
| `/api/chat`           | POST   | Create a new chat              |
| `/api/chat/<chat_id>` | DELETE | Delete a chat                  |

### **User Preferences**
| Endpoint             | Method | Description                         |
|----------------------|--------|-------------------------------------|
| `/api/preferences`  | GET    | Get user preferences               |
| `/api/preferences`  | PUT    | Update user preferences            |

---

## 🏆 Contributing

We welcome contributions! Follow these steps:
1. **Fork the repository**
2. **Create a new branch**: `git checkout -b feature-branch`
3. **Commit your changes**: `git commit -m "Feature description"`
4. **Push to your branch**: `git push origin feature-branch`
5. **Create a Pull Request**

---

## 📜 License

This project is licensed under the MIT License.

---

Happy Chatting! 🚀

