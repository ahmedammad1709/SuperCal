from app.models import User
from app.utils import engine
from app.models.user import Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    # NOTE: If you change models, re-run this script to update the database schema. 