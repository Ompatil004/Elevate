from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone
from fastapi import HTTPException
import logging
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class SafeWriteResult:
    """Result wrapper for safe database operations"""
    def __init__(self, matched_count: int, modified_count: int, upserted_id=None):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id

async def safe_update_one(
    collection,
    filter_query: dict,
    update_query: dict,
    upsert: bool = False,
    resource_name: str = "document"
) -> SafeWriteResult:
    """
    Safe MongoDB update with confirmation
    
    Args:
        collection: MongoDB collection
        filter_query: Query to find document
        update_query: Update operation
        upsert: Create if not exists
        resource_name: Name for error messages
    
    Returns:
        SafeWriteResult with counts
    
    Raises:
        HTTPException if write fails
    """
    try:
        result = await collection.update_one(filter_query, update_query, upsert=upsert)
        
        # Verify acknowledgment
        if not result.acknowledged:
            logger.error(f"MongoDB write not acknowledged for {resource_name}")
            raise HTTPException(
                status_code=503,
                detail=f"Database write failed for {resource_name}"
            )
        
        # Log results
        logger.debug(
            f"Update {resource_name}: matched={result.matched_count}, "
            f"modified={result.modified_count}, upserted={result.upserted_id}"
        )
        
        # Check if document was found (when not upserting)
        if not upsert and result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"{resource_name} not found"
            )
        
        return SafeWriteResult(
            matched_count=result.matched_count,
            modified_count=result.modified_count,
            upserted_id=result.upserted_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Safe update failed for {resource_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database operation failed: {str(e)}"
        )

async def safe_insert_one(
    collection,
    document: dict,
    resource_name: str = "document"
) -> ObjectId:
    """
    Safe MongoDB insert with confirmation
    
    Args:
        collection: MongoDB collection
        document: Document to insert
        resource_name: Name for error messages
    
    Returns:
        Inserted document ID
    
    Raises:
        HTTPException if insert fails
    """
    try:
        result = await collection.insert_one(document)
        
        if not result.acknowledged:
            logger.error(f"MongoDB insert not acknowledged for {resource_name}")
            raise HTTPException(
                status_code=503,
                detail=f"Database insert failed for {resource_name}"
            )
        
        logger.debug(f"Inserted {resource_name} with ID: {result.inserted_id}")
        
        return result.inserted_id
        
    except Exception as e:
        logger.error(f"Safe insert failed for {resource_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database operation failed: {str(e)}"
        )

async def safe_find_one(
    collection,
    filter_query: dict,
    resource_name: str = "document"
):
    """
    Safe MongoDB find with error handling
    
    Args:
        collection: MongoDB collection
        filter_query: Query to find document
        resource_name: Name for error messages
    
    Returns:
        Document or None
    """
    try:
        result = await collection.find_one(filter_query)
        return result
    except Exception as e:
        logger.error(f"Safe find failed for {resource_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database operation failed: {str(e)}"
        )

def db_operation_handler(max_retries: int = 2, timeout: int = 10):
    """
    Decorator for database operations with retry logic
    
    Args:
        max_retries: Number of retry attempts
        timeout: Timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request_id = _utcnow().strftime("%Y%m%d%H%M%S%f")
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    # Add timeout
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout
                    )
                    return result
                    
                except asyncio.TimeoutError:
                    logger.error(f"[{request_id}] Database operation timeout (attempt {attempt + 1})")
                    last_error = "Database timeout"
                    
                except Exception as e:
                    logger.error(f"[{request_id}] Database error (attempt {attempt + 1}): {e}")
                    last_error = str(e)
                    
                    # Don't retry on certain errors
                    if "E11000" in str(e):  # Duplicate key
                        raise HTTPException(
                            status_code=409,
                            detail="Duplicate key error"
                        )
                
                # Wait before retry (exponential backoff)
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 0.5
                    logger.info(f"[{request_id}] Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
            
            # All retries failed
            logger.error(f"[{request_id}] All {max_retries + 1} attempts failed")
            raise HTTPException(
                status_code=503,
                detail=f"Database operation failed after {max_retries + 1} attempts: {last_error}"
            )
        
        return wrapper
    return decorator
