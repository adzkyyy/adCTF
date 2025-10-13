# Precise Tick Scheduler using APScheduler
import threading
import time
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class PreciseTickScheduler:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Jakarta'))
        self.scheduler.start()
        self.job_id = 'tick_job'
        
    def start_challenge(self):
        """Start the challenge with immediate first tick and precise scheduling"""
        with self.app.app_context():
            try:
                # Get the tick duration from config
                from app.models import Config
                
                config = Config.query.first()
                if not config:
                    print("No config found!")
                    return False
                
                # Schedule subsequent ticks with precise timing
                self.schedule_next_tick(config.tick_duration_seconds)
                
                from app.controllers.tick_controller import next_tick
                
                # Execute first tick immediately
                print("Executing first tick to start the challenge...")
                result = next_tick()
                print(f"First tick result: {result}")
                
                return True
            except Exception as e:
                print(f"Error starting challenge: {e}")
                return False
    
    def schedule_next_tick(self, interval_seconds):
        """Schedule the next tick with precise timing"""
        # Remove existing job if any
        try:
            self.scheduler.remove_job(self.job_id)
        except:
            pass
        
        # Add new job with precise interval
        self.scheduler.add_job(
            func=self.execute_tick,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id=self.job_id,
            max_instances=1,
            coalesce=True,  # Coalesce missed executions
            misfire_grace_time=5  # Allow 5 seconds grace for missed executions
        )
        print(f"Scheduled ticks every {interval_seconds} seconds")
    
    def execute_tick(self):
        """Execute a single tick with error handling"""
        with self.app.app_context():
            try:
                from app.controllers.tick_controller import next_tick
                from app.models import Config
                
                config = Config.query.first()
                if not config or not config.challenge_started:
                    print("Challenge stopped, removing scheduled ticks")
                    self.stop_scheduling()
                    return
                
                print(f"Scheduler: Executing precise tick at {datetime.now(pytz.timezone('Asia/Jakarta'))}")
                result = next_tick()
                print(f"Scheduler: {result}")
                
            except Exception as e:
                print(f"Error in scheduled tick execution: {e}")
    
    def stop_scheduling(self):
        """Stop the tick scheduling"""
        try:
            self.scheduler.remove_job(self.job_id)
            print("Tick scheduling stopped")
        except:
            pass
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()

# Global scheduler instance
precise_scheduler = None

def get_scheduler(app, db):
    """Get or create the global scheduler instance"""
    global precise_scheduler
    if precise_scheduler is None:
        precise_scheduler = PreciseTickScheduler(app, db)
    return precise_scheduler