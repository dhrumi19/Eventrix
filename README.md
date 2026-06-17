🎉 Eventrix — Event Management System  
Python Django SQLite Bootstrap  

A full-stack event management web application built with Python and Django. Eventrix allows users to explore, book, and manage events while enabling admins to control the entire system. It also includes an automated reminder system to notify users about upcoming events.

🚀 Features  

User Side  
🔐 User registration and secure login/logout system  
📅 Browse and explore available events  
🎟️ Easy event booking system  
⏰ Automated reminders for upcoming events  
📋 View booking details and history  

Admin Side  
📊 Admin dashboard for monitoring system activity  
🛠️ Create, update, and delete events  
👥 Manage users and bookings  
⚙️ Full system control through Django admin panel  

🛠️ Tech Stack  

Layer        Technology  
Backend      Python 3.x, Django  
Database     SQLite  
Frontend     HTML, CSS, Bootstrap  
Tools        VS Code  

📂 Project Structure  

eventrix/  
├── accounts/           # User authentication module  
├── events/             # Event management module  
├── reminders/          # Reminder system  
├── templates/          # HTML templates  
├── static/             # CSS, JS, images  
├── db.sqlite3          # Database  
├── manage.py  
└── requirements.txt  

🔄 System Workflow  

User → Register/Login → Browse Events → Book Event → Receive Reminder  

🗄️ Database Models  

Model        Description  
User         Registered user details  
Event        Event information (title, date, location, etc.)  
Booking      Stores booking details of users  
Reminder     Handles event notification system  

⚙️ Installation  

# 1. Clone the repository  
git clone https://github.com/your-username/eventrix.git  
cd eventrix  

# 2. Create virtual environment  
python -m venv venv  

# Activate environment  
venv\Scripts\activate        # Windows  
source venv/bin/activate     # macOS/Linux  

# 3. Install dependencies  
pip install -r requirements.txt  

# 4. Run migrations  
python manage.py migrate  

# 5. Create superuser  
python manage.py createsuperuser  

# 6. Run server  
python manage.py runserver  

# Open in browser  
http://127.0.0.1:8000  

🎯 Future Enhancements  

💳 Payment Gateway Integration  
📱 Mobile App Version  
🔔 Real-time Notifications  
📊 Advanced Analytics Dashboard  

📚 Learning Outcomes  

- Hands-on experience with Django framework  
- Backend and database integration  
- Authentication system implementation  
- Real-world full-stack project development  

👩‍💻 Author  

Dhrumi Shah    
Passionate about Web Development & Data Analysis  
