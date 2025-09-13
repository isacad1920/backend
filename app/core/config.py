"""
Application configuration management using Pydantic settings.
"""
import secrets
from enum import Enum
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment types."""
    DEV = "DEV"
    STAGING = "STAGING"
    PROD = "PROD"

class Currency(str, Enum):
    """Supported currencies."""
    USD = "USD"
    SLSH = "SLSH"  # Somaliland Shilling
    ETB = "ETB"    # Ethiopian Birr

class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CASHIER = "CASHIER"
    INVENTORY_CLERK = "INVENTORY_CLERK"
    ACCOUNTANT = "ACCOUNTANT"

class Settings(BaseSettings):
    """Application settings configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8"
    )
    
    # Application Information
    app_name: str = "SOFinance POS System"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEV
    debug: bool = True
    
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/sofinance_db"
    
    # Security Configuration
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Password Configuration
    pwd_min_length: int = 8
    pwd_require_uppercase: bool = True
    pwd_require_lowercase: bool = True
    pwd_require_numbers: bool = True
    pwd_require_special: bool = True
    
    # CORS Configuration
    backend_cors_origins: str = ""
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Email Configuration
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    from_email: str | None = None
    
    # File Upload Configuration
    upload_path: str = "./uploads"
    max_file_size_mb: int = 10
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/gif"]
    allowed_document_types: list[str] = ["application/pdf", "text/csv", "application/vnd.ms-excel"]
    
    # Company Information
    company_name: str = "SOFinance Company"
    company_email: str = "info@sofinance.com"
    company_phone: str = "+1234567890"
    company_address: str = "123 Business Street"
    base_currency: Currency = Currency.USD
    timezone: str = "UTC"
    
    # Business Rules
    max_branches_per_company: int = 100
    max_users_per_branch: int = 50
    max_products_per_category: int = 1000
    default_tax_rate: float = 0.0
    
    # Audit Configuration
    enable_audit_logging: bool = True
    audit_retention_days: int = 365
    
    # Backup Configuration
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    backup_retention_days: int = 30

    # Restore / Backup operational safety limits
    max_concurrent_restore_jobs: int = 2
    enforce_restore_job_limit: bool = True  # Allow disabling in tests to avoid flaky 429s

    # Inventory thresholds
    default_low_stock_threshold: int = 10
    dead_stock_days_threshold: int = 90
    
    # API Configuration
    api_v1_str: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200
    
    # Session Configuration
    session_timeout_minutes: int = 480  # 8 hours
    max_concurrent_sessions: int = 5
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "app.log"
    log_max_size_mb: int = 100
    log_backup_count: int = 5
    
    # Feature Flags
    enable_multi_currency: bool = True
    enable_branch_orders: bool = True
    enable_customer_loyalty: bool = False
    enable_inventory_forecasting: bool = False
    enable_reports: bool = True
    enable_notifications: bool = True
    enable_key_mirroring: bool = False  # Disabled to enforce strict standardized envelope (no root key mirroring)
    # Response enrichment / observability
    enable_response_enrichment: bool = True
    response_enrichment_add_to_meta: bool = False
    response_enrichment_meta_namespace: str = "_ctx"
    include_correlation_id: bool = True
    include_app_version_meta: bool = True
    mirror_pagination_keys: bool = False  # Do not promote pagination/item keys to top-level
    
    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Validate and assemble CORS origins."""
        if isinstance(v, str) and v:
            return v
        return ""
    
    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v:
            raise ValueError("Database URL is required")
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("Only PostgreSQL databases are supported")
        return v
    
    @field_validator("upload_path")
    @classmethod
    def validate_upload_path(cls, v):
        """Ensure upload directory exists."""
        Path(v).mkdir(parents=True, exist_ok=True)
        return v
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        """Ensure secret key is strong enough."""
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v
    
    @property
    def database_settings(self) -> dict:
        """Get database connection settings."""
        return {
            "url": self.database_url,
            "echo": self.debug,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_timeout": 30,
            "pool_recycle": 1800,
        }
    
    @property
    def cors_settings(self) -> dict:
        """Get CORS settings for FastAPI."""
        origins = []
        if self.backend_cors_origins:
            origins = [i.strip() for i in self.backend_cors_origins.split(",")]
        return {
            "allow_origins": origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    
    @property
    def jwt_settings(self) -> dict:
        """Get JWT settings."""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "refresh_token_expire_days": self.refresh_token_expire_days,
        }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PROD
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEV
    
    @property
    def upload_settings(self) -> dict:
        """Get file upload settings."""
        return {
            "upload_path": self.upload_path,
            "max_file_size_mb": self.max_file_size_mb,
            "allowed_image_types": self.allowed_image_types,
            "allowed_document_types": self.allowed_document_types,
        }

# Global settings instance
settings = Settings()

# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment specific settings."""
    debug: bool = True
    log_level: str = "DEBUG"

class ProductionSettings(Settings):
    """Production environment specific settings."""
    debug: bool = False
    log_level: str = "WARNING"
    enable_audit_logging: bool = True
    backup_enabled: bool = True

class TestSettings(Settings):
    """Test environment specific settings."""
    debug: bool = True
    log_level: str = "DEBUG"
    database_url: str = "postgresql://test:test@localhost:5432/sofinance_test"

def get_settings() -> Settings:
    """Factory function to get settings based on environment."""
    env = Environment(settings.environment)
    
    if env == Environment.DEV:
        return DevelopmentSettings()
    elif env == Environment.PROD:
        return ProductionSettings()
    else:
        return settings

# Constants
class Constants:
    """Application constants."""
    
    # Default pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Cache TTL (seconds)
    CACHE_TTL_SHORT = 300      # 5 minutes
    CACHE_TTL_MEDIUM = 1800    # 30 minutes
    CACHE_TTL_LONG = 3600      # 1 hour
    
    # File size limits
    MAX_IMAGE_SIZE_MB = 5
    MAX_DOCUMENT_SIZE_MB = 10
    
    # Business rules
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    # Currency precision
    CURRENCY_DECIMAL_PLACES = 2
    
    # Date formats
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # System accounts (for journal entries)
    SYSTEM_ACCOUNTS = {
        "CASH": "Cash",
        "ACCOUNTS_RECEIVABLE": "Accounts Receivable",
        "INVENTORY": "Inventory",
        "SALES_REVENUE": "Sales Revenue",
        "COST_OF_GOODS_SOLD": "Cost of Goods Sold",
        "TAX_PAYABLE": "Tax Payable",
    }