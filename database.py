from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
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