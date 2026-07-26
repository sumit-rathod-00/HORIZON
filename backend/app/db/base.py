from app.db.base_class import Base

# Import all models so Alembic can discover them
from app.models.user import User  # noqa: F401