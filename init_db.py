import time
import sys
import os
from app import app, db
from app.models import User, Config
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

def wait_for_db(max_retries=60, delay=2):
    """Wait for database to be available with retries."""
    print(f"🔄 Waiting for database connection...")
    print(f"📊 Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    
    for attempt in range(max_retries):
        try:
            with app.app_context():
                # Try to connect to the database
                connection = db.engine.connect()
                connection.close()
                print(f"✅ Database connection successful on attempt {attempt + 1}")
                return True
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"⏳ Database not ready (attempt {attempt + 1}/{max_retries}). Retrying in {delay}s...")
                print(f"   Error: {str(e)[:100]}...")
                time.sleep(delay)
            else:
                print(f"❌ Failed to connect to database after {max_retries} attempts")
                print(f"❌ Final error: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error connecting to database: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {delay}s...")
                time.sleep(delay)
            else:
                return False
    
    return False

def initialize_database():
    """Initialize the database tables."""
    try:
        with app.app_context():
            print("🏗️  Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create admin user if it doesn't exist
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                print("👤 Creating admin user...")
                admin = User(
                    username=os.getenv('ADMIN_USERNAME', 'admin'), 
                    password_hash=generate_password_hash(os.getenv('ADMIN_PASSWORD', 'password')), 
                    is_admin=True,
                    is_active=True,
                    host_ip=""
                )
                db.session.add(admin)
                print(f"✅ Admin user '{admin.username}' created")
            else:
                print("ℹ️  Admin user already exists")
                
            # Create default configuration if it doesn't exist
            config = Config.query.first()
            if not config:
                print("⚙️  Creating default configuration...")
                default_config = Config(
                    challenge_started=False, 
                    ticks_count=0, 
                    tick_duration_seconds=60
                )
                db.session.add(default_config)
                print("✅ Default configuration created")
            else:
                print("ℹ️  Configuration already exists")
            
            db.session.commit()
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    print("🔄 Starting database initialization...")
    
    if not wait_for_db():
        print("❌ Cannot connect to database. Exiting.")
        sys.exit(1)
    
    if not initialize_database():
        print("❌ Database initialization failed. Exiting.")
        sys.exit(1)
    
    print("🎉 Database initialization completed successfully!")
