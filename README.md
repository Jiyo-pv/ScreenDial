# ScreenDial 🎥💬  
A Real-Time Screen Sharing & Collaboration Platform built with Django

ScreenDial is a lightweight real-time collaboration platform that enables users to create sessions, invite participants, chat live, exchange audio messages, and receive smart shortcut hints.

Designed with simplicity, performance, and usability in mind.

---

## 🚀 Features

✅ Real-time screen sharing (WebRTC)  
✅ Session-based meeting rooms  
✅ Invite participants by username  
✅ Join sessions via room code  
✅ Live chat system  
✅ Audio message support  
✅ Smart command hint engine  
✅ Session visibility controls  
✅ Participant management (Accept / Reject / Kick)  
✅ Clean modern UI  

---

## 🧠 Smart Hint Engine

ScreenDial includes a command suggestion system.

When users type common actions like:

copy  
paste  
screenshot  
task manager  

They receive instant Windows shortcut hints.

Example:

Ctrl + C → Copy selected item  
Win + Shift + S → Screenshot  

Optimized for performance using simple keyword matching.

---

## 🛠️ Tech Stack

### Backend
- Django  
- Django Channels (WebSockets)  
- SQLite / PostgreSQL  

### Frontend
- HTML5  
- CSS3  
- JavaScript  
- WebRTC API  

### Realtime Communication
- WebSockets  
- WebRTC  

---

## ⚡ Core Concepts

ScreenDial revolves around:

- **Sessions** → Meeting rooms  
- **Participants** → Users inside sessions  
- **Invitations** → Host-controlled access  
- **Join Requests** → Room-code based entry  
- **Realtime Events** → WebSocket messaging  

---

## 🏗️ Architecture Overview

User Actions → Django Views → Database  
             → WebSockets (Channels)  
             → WebRTC Peer Connections  

Realtime operations handled asynchronously via Django Channels.

---

## 🔧 Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/screendial.git
cd screendial
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Populate Command Suggestions

```bash
python manage.py populate_commands
```

### 6️⃣ Start Server

```bash
python manage.py runserver
```

---

## 🎯 Usage Flow

### ✅ Host Flow

1. Create Session  
2. Invite Participants  
3. Start Screen Share  
4. Manage Participants  

---

### ✅ Participant Flow

1. Join via Room Code OR Invitation  
2. Chat / Audio / View Screen  

---

## 🎛️ Session Controls

Hosts can:

✅ Toggle suggestions system  
✅ Control session visibility  
✅ Accept / Reject join requests  
✅ Kick participants  
✅ Hide screen share per user  

---

## ⚡ Performance Design

✔ Lightweight keyword matching  
✔ Minimal database queries  
✔ No heavy algorithms  
✔ Optimized realtime communication  

Designed for responsiveness and efficiency.

---

## 🔮 Future Improvements

🚀 Planned Enhancements:

- Typo-tolerant hint matching  
- Screen recording  
- File transfer  
- Role permissions  
- UI theme customization  

---

## 👨‍💻 Developer Notes

ScreenDial prioritizes:

✅ Simplicity  
✅ Real-time responsiveness  
✅ Clean UX  
✅ Low computational overhead  

---

## 📜 License

This project is for educational and development purposes.

---

## ✨ Author

Developed by **[JIYO  P V]]**  
Django • Realtime Systems • WebRTC
