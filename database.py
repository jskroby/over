from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

# Create Session class
Session = sessionmaker(bind=engine)

class SystemMetrics(Base):
    __tablename__ = 'system_metrics'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    ollama_status = Column(Boolean)

class AgentStatus(Base):
    __tablename__ = 'agent_status'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    status = Column(Boolean)
    last_updated = Column(DateTime, default=datetime.utcnow)
    current_task = Column(String)
    code_repository = Column(String)

class CodeSnippet(Base):
    __tablename__ = 'code_snippets'

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(Text)
    language = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    agent_name = Column(String)
    status = Column(String)  # crawled, edited, deployed
    binary_data = Column(LargeBinary, nullable=True)
    file_type = Column(String)

class AgentTask(Base):
    __tablename__ = 'agent_tasks'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    task_type = Column(String)  # crawl, process, deploy
    task_status = Column(String)  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    conversation_id = Column(String)
    message_type = Column(String)

class TaskSchedule(Base):
    __tablename__ = 'task_schedules'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    task_name = Column(String)
    task_description = Column(Text)
    schedule_type = Column(String)  # once, daily, weekly, monthly
    schedule_time = Column(DateTime)
    parameters = Column(JSON)  # Store task-specific parameters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime)

class DeploymentLog(Base):
    __tablename__ = 'deployment_logs'

    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    deployment_status = Column(String)
    commit_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    github_url = Column(String)

class WorkspaceFolder(Base):
    __tablename__ = 'workspace_folders'

    id = Column(Integer, primary_key=True)
    folder_name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
def init_db():
    Base.metadata.create_all(engine)