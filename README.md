# Chomchonlink

**Type**: Web Application  
**Language**: Python (Django Framework)  
**Course Project**: Full Stack Software Development (DSI202)

### 🔍 About the Project

**Chomchonlink** is a web application inspired by **Meetup**, designed to strengthen community engagement within the **Khlong Luang** area — especially between local residents and university students.  
It provides a platform where users can create, discover, and join local events, groups, and activities based on shared interests.

### 🎯 Project Purpose

- Encourage meaningful connections and friendships among community members  
- Promote local attractions, activities, and cultural traditions  
- Help new residents and students integrate more easily into the community

### 💡 Key Features

👥 Create and join groups based on shared interests (e.g., hiking, cooking, language exchange)  
📅 Browse upcoming local events with intuitive search and filter options  
🧑‍💼 Event creation and management tools for local organizers and businesses  
🔍 Discover cultural activities, volunteer opportunities, and community news  
🔐 User authentication and profile system (residents, students, organizers)

### 📚 Example User Stories

- *"As a new university student, I want to join local events so that I can meet new people and feel connected to the area."*  
- *"As a local resident, I want to find cultural events and festivals so I can participate in my community's traditions."*  
- *"As a retiree, I want to discover volunteer opportunities to stay active and contribute."*  
- *"As a local business owner, I want to promote my events to reach more people in the neighborhood."*  
- *"As someone who enjoys outdoor activities, I want to connect with people who have similar hobbies."*

#### ✅ Step-by-step Instructions

1. **Navigate to the Django project folder**  เข้าไปในโฟลเดอร์ที่มี Django Projec
```bash
cd dsi202/myproject
```

2. **Create a virtual environment** (only needed the first time) สร้าง Virtual Environment (ครั้งแรกเท่านั้น)
```bash
python3 -m venv env
```

3. **Activate the virtual environment**  เปิดใช้งาน Virtual Environment
```bash
source env/bin/activate
```

4. **Install required dependencies** ติดตั้งไลบรารีที่จำเป็น
```bash
pip install -r ../requirements_django.txt
```

5. **Apply database migrations** สร้างฐานข้อมูลด้วย migration
bash
CopyEdit

```bash
python manage.py migrate
```

6. **Start the development server**   รันเซิร์ฟเวอร์
```bash
python manage.py runserver
```

7. **Visit the web app in your browser**
```
http://127.0.0.1:8000
```

#### 🛑 Troubleshooting

- Ensure you're inside the folder that contains `manage.py`
- If `env/bin/activate` doesn't exist, you may need to re-create the virtual environment
- Use `python3` instead of `python` if `python` points to version 2.x
