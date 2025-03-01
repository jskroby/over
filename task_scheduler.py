import schedule
import time
import threading
from datetime import datetime, timedelta
from database import Session, TaskSchedule, AgentTask
from logger_config import logger

class TaskScheduler:
    def __init__(self):
        self.scheduler_thread = None
        self.is_running = False
        
    def start(self):
        """Start the scheduler in a background thread"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            logger.info("Task scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
            logger.info("Task scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            self._check_and_execute_tasks()
            time.sleep(60)  # Check every minute

    def _check_and_execute_tasks(self):
        """Check for due tasks and execute them"""
        try:
            session = Session()
            now = datetime.utcnow()
            
            # Get all active tasks that are due
            due_tasks = session.query(TaskSchedule).filter(
                TaskSchedule.is_active == True,
                TaskSchedule.next_run <= now
            ).all()

            for task in due_tasks:
                self._execute_task(task)
                self._update_next_run(task)

            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Error in task scheduler: {e}")

    def _execute_task(self, task):
        """Execute a scheduled task"""
        try:
            # Create agent task record
            session = Session()
            agent_task = AgentTask(
                agent_name=task.agent_name,
                task_type='scheduled',
                task_status='running',
                result=f"Executing scheduled task: {task.task_name}"
            )
            session.add(agent_task)
            
            # Update task's last run time
            task.last_run = datetime.utcnow()
            
            session.commit()
            session.close()
            
            logger.info(f"Executed scheduled task: {task.task_name} for agent: {task.agent_name}")
        except Exception as e:
            logger.error(f"Error executing task {task.task_name}: {e}")

    def _update_next_run(self, task):
        """Calculate and update the next run time for a task"""
        now = datetime.utcnow()
        
        if task.schedule_type == 'once':
            task.is_active = False
        elif task.schedule_type == 'daily':
            task.next_run = now + timedelta(days=1)
        elif task.schedule_type == 'weekly':
            task.next_run = now + timedelta(weeks=1)
        elif task.schedule_type == 'monthly':
            # Add roughly a month (30 days)
            task.next_run = now + timedelta(days=30)

    def add_task(self, agent_name, task_name, task_description, schedule_type, schedule_time, parameters=None):
        """Add a new scheduled task"""
        try:
            session = Session()
            task = TaskSchedule(
                agent_name=agent_name,
                task_name=task_name,
                task_description=task_description,
                schedule_type=schedule_type,
                schedule_time=schedule_time,
                parameters=parameters or {},
                next_run=schedule_time
            )
            session.add(task)
            session.commit()
            session.close()
            logger.info(f"Added new scheduled task: {task_name} for agent: {agent_name}")
            return True
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return False

    def get_scheduled_tasks(self, agent_name=None):
        """Get all scheduled tasks, optionally filtered by agent"""
        try:
            session = Session()
            query = session.query(TaskSchedule)
            if agent_name:
                query = query.filter_by(agent_name=agent_name)
            tasks = query.order_by(TaskSchedule.next_run).all()
            session.close()
            return tasks
        except Exception as e:
            logger.error(f"Error getting scheduled tasks: {e}")
            return []
