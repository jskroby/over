import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from github import Github
from logger_config import logger
import streamlit as st
from requests_oauthlib import OAuth2Session
import json

class StorageManager:
    def __init__(self):
        self.gdrive_service = None
        self.github_client = None

        # GitHub OAuth settings
        self.github_client_id = os.getenv('GITHUB_CLIENT_ID')
        self.github_client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        self.github_auth_url = 'https://github.com/login/oauth/authorize'
        self.github_token_url = 'https://github.com/login/oauth/access_token'
        self.github_scope = ['repo']

        # Google Drive OAuth settings
        self.gdrive_scopes = ['https://www.googleapis.com/auth/drive.file']

    def initialize_github_oauth(self):
        """Initialize GitHub OAuth flow"""
        try:
            github_oauth = OAuth2Session(
                self.github_client_id,
                scope=self.github_scope,
                redirect_uri=st.secrets["github_redirect_uri"]
            )
            auth_url, state = github_oauth.authorization_url(self.github_auth_url)
            st.session_state['github_oauth_state'] = state
            return auth_url
        except Exception as e:
            logger.error(f"Failed to initialize GitHub OAuth: {e}")
            return None

    def initialize_gdrive_oauth(self):
        """Initialize Google Drive OAuth flow"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                self.gdrive_scopes
            )
            auth_url = flow.authorization_url()[0]
            return auth_url
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive OAuth: {e}")
            return None

    def handle_github_callback(self, code, state):
        """Handle GitHub OAuth callback"""
        try:
            if state != st.session_state.get('github_oauth_state'):
                return False

            github_oauth = OAuth2Session(
                self.github_client_id,
                state=state,
                redirect_uri=st.secrets["github_redirect_uri"]
            )
            token = github_oauth.fetch_token(
                self.github_token_url,
                client_secret=self.github_client_secret,
                code=code
            )
            st.session_state['github_token'] = token
            self.github_client = Github(token['access_token'])
            return True
        except Exception as e:
            logger.error(f"Failed to handle GitHub callback: {e}")
            return False

    def handle_gdrive_callback(self, code):
        """Handle Google Drive OAuth callback"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                self.gdrive_scopes,
                redirect_uri=st.secrets["gdrive_redirect_uri"]
            )
            flow.fetch_token(code=code)
            self.gdrive_service = build('drive', 'v3', credentials=flow.credentials)
            st.session_state['gdrive_credentials'] = flow.credentials.to_json()
            return True
        except Exception as e:
            logger.error(f"Failed to handle Google Drive callback: {e}")
            return False

    def upload_to_drive(self, file_path, folder_id=None):
        """Upload a file to Google Drive"""
        try:
            if not self.gdrive_service:
                return None

            file_metadata = {'name': os.path.basename(file_path)}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            media = MediaFileUpload(file_path)
            file = self.gdrive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            logger.info(f"File uploaded to Drive: {file.get('id')}")
            return file.get('id')
        except Exception as e:
            logger.error(f"Failed to upload to Drive: {e}")
            return None

    def backup_agent_data(self, agent_name, data_path):
        """Backup agent data to both Drive and GitHub"""
        try:
            # Upload to Drive if authenticated
            if self.gdrive_service:
                drive_id = self.upload_to_drive(data_path)
                logger.info(f"Backed up to Drive: {drive_id}")

            # Push to GitHub if authenticated
            if self.github_client:
                repo_name = f"agent-{agent_name}-backup"
                user = self.github_client.get_user()
                try:
                    repo = user.get_repo(repo_name)
                except:
                    repo = user.create_repo(repo_name, description=f"Backup repository for {agent_name}")

                with open(data_path, 'r') as file:
                    content = file.read()

                repo.create_file(
                    os.path.basename(data_path),
                    "Automated backup",
                    content
                )
                logger.info(f"Backed up to GitHub: {repo_name}")

            return True
        except Exception as e:
            logger.error(f"Failed to backup agent data: {e}")
            return False