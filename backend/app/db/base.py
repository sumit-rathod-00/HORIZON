from app.db.base_class import Base

# Import all models so Alembic can discover them
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.asset import Asset  # noqa: F401
from app.models.vulnerability import Vulnerability  # noqa: F401
from app.models.scan import Scan  # noqa: F401
from app.models.scan_result import ScanResult  # noqa: F401
from app.models.device import Device  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
