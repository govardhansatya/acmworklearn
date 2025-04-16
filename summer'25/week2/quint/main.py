from agents.core_crew import crew
from data.db import Base, engine
from personal_assistant.backend.tasks import check_and_assign_tasks

def init():
    print("🔧 Initializing database and crew...")
    Base.metadata.create_all(bind=engine)
    check_and_assign_tasks()
    crew.run()

if __name__ == "__main__":
    init()
