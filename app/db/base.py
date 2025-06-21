"""
SQLAlchemy engine, session, and custom query class for the AI Stock Portfolio Platform Backend.

This module configures the engine and session factory with performance optimizations and provides a custom Query class for advanced ORM operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine with optimized settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Maximum number of connections to keep
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
    echo=settings.SQL_ECHO,  # Enable SQL query logging in debug mode
    # Performance optimizations
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "application_name": "trading_app",  # Application name for monitoring
        "options": "-c statement_timeout=30000"  # Query timeout in milliseconds
    }
)

# Create session factory with optimized settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,  # Prevent expired object access after commit
    query_cls=Query  # Use optimized query class
)

# Create base class for models
Base = declarative_base()

# Custom query class with optimizations
class Query(BaseQuery):
    """
    Custom query class with advanced ORM optimizations and convenience methods.
    """
    def get_or_404(self, ident):
        """
        Get object by id or raise 404 if not found.

        Args:
            ident: Primary key identifier.
        Returns:
            ORM object.
        Raises:
            HTTPException: If object is not found.
        """
        rv = self.get(ident)
        if rv is None:
            raise HTTPException(status_code=404, detail="Object not found")
        return rv

    def first_or_404(self):
        """
        Get first object or raise 404 if not found.

        Returns:
            ORM object.
        Raises:
            HTTPException: If object is not found.
        """
        rv = self.first()
        if rv is None:
            raise HTTPException(status_code=404, detail="Object not found")
        return rv

    def paginate(self, page=None, per_page=None, error_out=True, max_per_page=None):
        """
        Return paginated results for a query.

        Args:
            page (int, optional): Page number.
            per_page (int, optional): Results per page.
            error_out (bool, optional): Raise error if page not found.
            max_per_page (int, optional): Maximum results per page.
        Returns:
            dict: Pagination metadata and items.
        Raises:
            HTTPException: If page is not found.
        """
        if page is None:
            page = 1
        if per_page is None:
            per_page = 20
        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        items = self.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1 and error_out:
            raise HTTPException(status_code=404, detail="Page not found")

        # Get total count efficiently
        total = self.order_by(None).count()

        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }

    def with_entities(self, *entities):
        """Optimize query by selecting only needed columns"""
        return self.options(load_only(*entities))

    def with_relationships(self, *relationships):
        """Eager load relationships to avoid N+1 queries"""
        return self.options(joinedload(*relationships))

    def with_count(self, *relationships):
        """Add count of relationships to avoid N+1 queries"""
        return self.options(selectinload(*relationships))

    def with_exists(self, *relationships):
        """Add exists check for relationships to avoid N+1 queries"""
        return self.options(exists(*relationships))

    def with_defer(self, *columns):
        """Defer loading of columns until needed"""
        return self.options(defer(*columns))

    def with_undefer(self, *columns):
        """Undefer loading of columns"""
        return self.options(undefer(*columns))

    def with_undefer_group(self, group):
        """Undefer loading of column group"""
        return self.options(undefer_group(group))

    def with_raiseload(self, *relationships):
        """Raise error if relationship is accessed"""
        return self.options(raiseload(*relationships))

    def with_selectinload(self, *relationships):
        """Use selectin loading for relationships"""
        return self.options(selectinload(*relationships))

    def with_joinedload(self, *relationships):
        """Use joined loading for relationships"""
        return self.options(joinedload(*relationships))

    def with_subqueryload(self, *relationships):
        """Use subquery loading for relationships"""
        return self.options(subqueryload(*relationships))

    def with_lazyload(self, *relationships):
        """Use lazy loading for relationships"""
        return self.options(lazyload(*relationships))

    def with_noload(self, *relationships):
        """Disable loading of relationships"""
        return self.options(noload(*relationships))

    def with_dynamic(self, *relationships):
        """Use dynamic loading for relationships"""
        return self.options(dynamic(*relationships))

    def with_contains_eager(self, *relationships):
        """Use contains eager loading for relationships"""
        return self.options(contains_eager(*relationships))

    def with_immediateload(self, *relationships):
        """Use immediate loading for relationships"""
        return self.options(immediateload(*relationships))

    def with_selectin_polymorphic(self, *entities):
        """Use selectin polymorphic loading for entities"""
        return self.options(selectin_polymorphic(*entities))

    def with_joined_polymorphic(self, *entities):
        """Use joined polymorphic loading for entities"""
        return self.options(joined_polymorphic(*entities))

    def with_polymorphic(self, *entities):
        """Use polymorphic loading for entities"""
        return self.options(polymorphic(*entities))

    def with_undefer_polymorphic(self, *entities):
        """Undefer polymorphic loading for entities"""
        return self.options(undefer_polymorphic(*entities))

    def with_raiseload_polymorphic(self, *entities):
        """Raise error if polymorphic entity is accessed"""
        return self.options(raiseload_polymorphic(*entities))

    def with_selectinload_polymorphic(self, *entities):
        """Use selectin polymorphic loading for entities"""
        return self.options(selectinload_polymorphic(*entities))

    def with_joinedload_polymorphic(self, *entities):
        """Use joined polymorphic loading for entities"""
        return self.options(joinedload_polymorphic(*entities))

    def with_subqueryload_polymorphic(self, *entities):
        """Use subquery polymorphic loading for entities"""
        return self.options(subqueryload_polymorphic(*entities))

    def with_lazyload_polymorphic(self, *entities):
        """Use lazy polymorphic loading for entities"""
        return self.options(lazyload_polymorphic(*entities))

    def with_noload_polymorphic(self, *entities):
        """Disable polymorphic loading for entities"""
        return self.options(noload_polymorphic(*entities))

    def with_dynamic_polymorphic(self, *entities):
        """Use dynamic polymorphic loading for entities"""
        return self.options(dynamic_polymorphic(*entities))

    def with_contains_eager_polymorphic(self, *entities):
        """Use contains eager polymorphic loading for entities"""
        return self.options(contains_eager_polymorphic(*entities))

    def with_immediateload_polymorphic(self, *entities):
        """Use immediate polymorphic loading for entities"""
        return self.options(immediateload_polymorphic(*entities)) 