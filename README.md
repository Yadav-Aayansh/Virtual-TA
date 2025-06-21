# 🤖 **Virtual-TA**

Virtual-TA is a Retrieval-Augmented Generation (RAG) application designed to assist students and instructors in Tools in Data Science courses by leveraging large language models and vector databases to provide intelligent, context-aware responses.

---

## 📑 Table of Contents

- [📘 Project Overview](#project-overview)
- [⚙️ Prerequisites](#prerequisites)
- [🗂️ Project Directory Structure](#project-directory-structure)
- [💻 Setup & Local Development](#setup--local-development)
  - [🚀 Option 1: Quick Start with Pre-processed Data](#option-1-quick-start-with-pre-processed-data)
  - [🔧 Option 2: Complete Setup from Scratch](#option-2-complete-setup-from-scratch)
- [☁️ Cloud Deployment (AWS)](#cloud-deployment-aws)
- [📄 License](#license)

---

## 📘 Project Overview

Virtual-TA integrates course materials and discussion forum data to deliver relevant answers to student queries. It uses embeddings for efficient retrieval and advanced language models for response generation. ✨

---

## ⚙️ Prerequisites

Ensure the following are installed and configured:

- **Git**: For cloning the repository.
- **Python 3.8+**: Required to run the application.
- **Virtual Environment**: Recommended for dependency isolation.
- **API Keys**:
  - `AIPROXY_API_KEY`
  - `TOGETHER_AI_API_KEY`

---

## 🗂️ Project Directory Structure

```plaintext
Virtual-TA
├── api/
│   ├── core.py
│   ├── course.py
│   ├── discourse.py
│   ├── main.py
│   └── utils.py
├── data/
│   ├── course_index.faiss
│   ├── course_metadata.json
│   ├── discourse_index.faiss
│   └── discourse_metadata.json
├── scripts/
│   ├── 1_topics_fetcher.py
│   ├── 2_topics_cleaner.py
│   ├── 3_topics_merger.py
│   ├── 4_topics_answer.py
│   ├── 5_content_merger.py
│   ├── 6_topics_embedding.py
│   └── 7_content_embedding.py
├── README.md
├── requirements.txt
└── LICENSE
```

---

## 💻 Setup & Local Development

### 🚀 Option 1: Quick Start with Pre-processed Data

Use pre-processed data for a fast setup:

1. **Navigate to the API directory**:

   ```bash
   cd api
   ```

2. **Start the server**:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 6969
   ```

### 🔧 Option 2: Complete Setup from Scratch

Process and embed data from scratch:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Private-Aayansh/Virtual-TA.git
   cd Virtual-TA
   ```

2. **Set up a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Data fetching and embedding**:

   - **Fetch topics**:
     ```bash
     python scripts/1_topics_fetcher.py
     ```
   - **Clean topics**:
     ```bash
     python scripts/2_topics_cleaner.py
     ```
   - **Merge topics**:
     ```bash
     python scripts/3_topics_merger.py
     ```
   - **Fetch questions and replies**:
     ```bash
     python scripts/4_topics_answer.py
     ```
   - **Clone course content**:
     ```bash
     git clone https://github.com/sanand0/tools-in-data-science-public.git raw-data/cloned
     ```
   - **Merge course content**:
     ```bash
     python scripts/5_content_merger.py
     ```
   - **Create topic embeddings**:
     ```bash
     python scripts/6_topics_embedding.py
     ```
   - **Create content embeddings**:
     ```bash
     python scripts/7_content_embedding.py
     ```

5. **Navigate to the API directory**:

   ```bash
   cd api
   ```

6. **Start the server**:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 6969
   ```

---

## ☁️ Cloud Deployment (AWS)

Deploy Virtual-TA on AWS EC2 for scalability:

1. **Launch an EC2 instance**:

   - Use Ubuntu 22.04 LTS.
   - Select an instance type (e.g., `t3.micro`).
   - Open ports 22 (SSH) and 8000 (API).

2. **SSH into the instance**:

   ```bash
   ssh -i /path/to/key.pem ubuntu@YOUR_EC2_PUBLIC_IP
   ```

3. **Install dependencies**:

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git
   ```

4. **Clone the repository**:

   ```bash
   git clone https://github.com/Private-Aayansh/Virtual-TA.git
   cd Virtual-TA
   ```

5. **Set up a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

6. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

7. **Run the application with Gunicorn**:

   - Create a service file at `/etc/systemd/system/virtual-ta.service`:
     ```ini
     [Unit]
     Description=Gunicorn server for Virtual-TA
     After=network.target

     [Service]
     User=ubuntu
     Group=ubuntu
     WorkingDirectory=/home/ubuntu/Virtual-TA/api
     Environment="PATH=/home/ubuntu/Virtual-TA/venv/bin"
     Environment="PYTHONPATH=/home/ubuntu/Virtual-TA/api"
     ExecStart=/home/ubuntu/Virtual-TA/venv/bin/gunicorn \
       main:app \
       --workers 2 \
       --threads 16 \
       --bind 0.0.0.0:8000
     Restart=always
     RestartSec=3
     TimeoutStopSec=10

     [Install]
     WantedBy=multi-user.target
     ```
   - **Start and enable the service**:
     ```bash
     sudo systemctl daemon-reload
     sudo systemctl start virtual-ta
     sudo systemctl enable virtual-ta
     ```

8. **Access the application**:

   - Visit `http://<ec2-public-ip>:8000` 🚀

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
