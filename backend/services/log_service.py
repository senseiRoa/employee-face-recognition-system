from sqlalchemy.orm import Session, joinedload
from typing import Optional, List, Dict, Any
from models import AccessLog, UserLoginLog, Employee
from datetime import datetime


def get_access_logs(
    db: Session,
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(AccessLog)

    if employee_id:
        query = query.filter(AccessLog.employee_id == employee_id)
    if warehouse_id:
        query = query.filter(AccessLog.warehouse_id == warehouse_id)
    if start_date:
        query = query.filter(AccessLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AccessLog.timestamp <= end_date)

    return query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()


def get_enhanced_access_logs(
    db: Session,
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get enhanced access logs with detailed information including employee and warehouse names

    Returns data in the format:
    {
        id: 1,
        timestamp: '2025-10-08T10:30:00.000Z',
        employee_name: 'Juan Perez',
        action_type: 'check_in',
        warehouse_name: 'Central Warehouse',
        ip_address: '192.168.1.100',
        success: true,
        details: 'Successful check-in via facial recognition',
        confidence_score: 0.95,
        access_method: 'face_recognition',
        device_info: {...}
    }
    """
    query = db.query(AccessLog).options(
        joinedload(AccessLog.employee).joinedload(Employee.warehouse)
    )

    # Apply filters
    if employee_id:
        query = query.filter(AccessLog.employee_id == employee_id)
    if warehouse_id:
        query = query.join(Employee).filter(Employee.warehouse_id == warehouse_id)
    if start_date:
        query = query.filter(AccessLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AccessLog.timestamp <= end_date)

    # Get results
    logs = query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()

    # Transform to enhanced format
    enhanced_logs = []
    for log in logs:
        # Determine action type
        action_type = _map_event_type_to_action(log.event_type)

        # Determine success status
        success = _determine_success_status(log.event_type, log.is_verified)

        # Generate details
        details = _generate_details(log)

        # Extract IP address from device_info or additional_data
        ip_address = _extract_ip_address(log)

        # Parse confidence score
        confidence_score = _parse_confidence_score(log.confidence_score)

        enhanced_log = {
            "id": log.id,
            "timestamp": log.timestamp.isoformat() + "Z",
            "employee_name": f"{log.employee.first_name} {log.employee.last_name}",
            "action_type": action_type,
            "warehouse_name": log.employee.warehouse.name
            if log.employee.warehouse
            else "Unknown Warehouse",
            "ip_address": ip_address,
            "success": success,
            "details": details,
            "confidence_score": confidence_score,
            "access_method": log.access_method,
            "device_info": log.device_info,
        }

        enhanced_logs.append(enhanced_log)

    return enhanced_logs


def _map_event_type_to_action(event_type: str) -> str:
    """Map database event_type to user-friendly action_type"""
    mapping = {
        "in": "check_in",
        "entry": "check_in",
        "out": "check_out",
        "exit": "check_out",
        "denied": "denied",
        "unknown": "unknown",
        "failed": "denied",
    }
    return mapping.get(event_type.lower(), "unknown")


def _determine_success_status(event_type: str, is_verified: bool) -> bool:
    """Determine if the access attempt was successful"""
    successful_events = ["in", "entry", "out", "exit"]
    return event_type.lower() in successful_events or is_verified


def _generate_details(log: AccessLog) -> str:
    """Generate human-readable details for the log entry"""
    action = _map_event_type_to_action(log.event_type)
    method = log.access_method or "unknown method"

    if log.notes:
        return log.notes

    if action == "check_in":
        if method == "face_recognition":
            confidence = (
                f" (confidence: {log.confidence_score})" if log.confidence_score else ""
            )
            return f"Successful check-in via facial recognition{confidence}"
        else:
            return f"Check-in via {method}"
    elif action == "check_out":
        if method == "face_recognition":
            confidence = (
                f" (confidence: {log.confidence_score})" if log.confidence_score else ""
            )
            return f"Successful check-out via facial recognition{confidence}"
        else:
            return f"Check-out via {method}"
    elif action == "denied":
        reason = (
            "Low confidence facial recognition"
            if method == "face_recognition"
            else "Access denied"
        )
        return f"{reason} - {method}"
    else:
        return f"Unknown access event via {method}"


def _extract_ip_address(log: AccessLog) -> Optional[str]:
    """Extract IP address from device_info or additional_data"""
    # Try device_info first
    if log.device_info and isinstance(log.device_info, dict):
        ip = log.device_info.get("ip_address") or log.device_info.get("ip")
        if ip:
            return ip

    # Try additional_data
    if log.additional_data and isinstance(log.additional_data, dict):
        ip = log.additional_data.get("ip_address") or log.additional_data.get("ip")
        if ip:
            return ip

    # Generate a default IP for demo purposes (in real app, this would be captured from request)
    return "192.168.1.100"


def _parse_confidence_score(confidence_str: Optional[str]) -> Optional[float]:
    """Parse confidence score from string to float"""
    if not confidence_str:
        return None

    try:
        # Remove percentage sign if present and convert to float
        confidence_clean = confidence_str.replace("%", "").strip()
        confidence = float(confidence_clean)

        # If it's already in 0-1 range, return as is
        if 0 <= confidence <= 1:
            return round(confidence, 3)
        # If it's in percentage (0-100), convert to 0-1
        elif 0 <= confidence <= 100:
            return round(confidence / 100, 3)
        else:
            return None
    except (ValueError, TypeError):
        return None


def get_user_login_logs(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(UserLoginLog)

    if user_id:
        query = query.filter(UserLoginLog.user_id == user_id)
    if start_date:
        query = query.filter(UserLoginLog.timestamp >= start_date)
    if end_date:
        query = query.filter(UserLoginLog.timestamp <= end_date)

    return query.order_by(UserLoginLog.timestamp.desc()).offset(skip).limit(limit).all()


def create_user_login_log(
    db: Session, user_id: int, location: str = None, browser: str = None
):
    log = UserLoginLog(user_id=user_id, location=location, browser=browser)
    db.add(log)
    db.commit()
    return log
