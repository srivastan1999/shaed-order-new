"""
Response models for API endpoints
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FieldChangeRow(BaseModel):
    """Single row of field comparison data"""
    Order_Number: Optional[str] = None
    Body_Code: Optional[str] = None
    Model_Year: Optional[int] = None
    Customer_Name: Optional[str] = None
    VIN: Optional[str] = None
    Field_Name: str
    Old_Value: Optional[str] = None
    New_Value: Optional[str] = None
    old_date: str
    new_date: str


class FieldComparisonResponse(BaseModel):
    """Response model for field comparison endpoint"""
    data: List[Dict[str, Any]] = Field(..., description="List of field change records")
    total: int = Field(..., description="Total number of changes")
    limit: Optional[int] = Field(None, description="Limit applied to results")
    offset: int = Field(0, description="Offset applied to results")
    old_date: str = Field(..., description="Old date used in comparison")
    new_date: str = Field(..., description="New date used in comparison")


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")


class FieldStatistics(BaseModel):
    """Statistics for a single field"""
    field_name: str
    change_count: int


class ComparisonStatsResponse(BaseModel):
    """Response model for statistics endpoint"""
    total_changes: int = Field(..., description="Total number of field changes")
    unique_orders_affected: int = Field(..., description="Number of unique orders with changes")
    unique_fields_changed: int = Field(..., description="Number of unique fields that changed")
    field_statistics: List[FieldStatistics] = Field(..., description="Statistics per field")
    old_date: str = Field(..., description="Old date used in comparison")
    new_date: str = Field(..., description="New date used in comparison")

