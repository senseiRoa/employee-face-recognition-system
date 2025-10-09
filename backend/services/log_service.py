from sqlalchemy.orm import Session, joinedload
from typing import Optional, List, Dict, Any, Tuple
from models import AccessLog, UserLoginLog, Employee
from datetime import datetime
import pandas as pd
import io


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
        "in": "clock_in",
        "entry": "clock_in",
        "out": "clock_out",
        "exit": "clock_out",
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

    if action == "clock_in":
        if method == "face_recognition":
            confidence = (
                f" (confidence: {log.confidence_score})" if log.confidence_score else ""
            )
            return f"Successful clock-in via facial recognition{confidence}"
        else:
            return f"Clock-in via {method}"
    elif action == "clock_out":
        if method == "face_recognition":
            confidence = (
                f" (confidence: {log.confidence_score})" if log.confidence_score else ""
            )
            return f"Successful clock-out via facial recognition{confidence}"
        else:
            return f"Clock-out via {method}"
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


def get_export_excel_enhanced_access_logs(
    db: Session,
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 1000,  # Higher limit for exports
) -> List[Dict[str, Any]]:
    """
    Get enhanced access logs optimized for Excel export with all necessary data

    Similar to get_enhanced_access_logs but with optimizations for bulk export:
    - Higher default limit (1000 vs 100)
    - Additional formatting for Excel compatibility
    - Comprehensive data inclusion

    Returns data in the same format as get_enhanced_access_logs:
    {
        id: 1,
        timestamp: '2025-10-08T10:30:00.000Z',
        employee_name: 'Juan Perez',
        action_type: 'clock_in',
        warehouse_name: 'Central Warehouse',
        ip_address: '192.168.1.100',
        success: true,
        details: 'Successful clock-in via facial recognition',
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

    # Get results with optimized ordering for exports
    logs = query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()

    # Transform to enhanced format optimized for export
    enhanced_logs = []
    for log in logs:
        # Determine action type
        action_type = _map_event_type_to_action(log.event_type)

        # Determine success status
        success = _determine_success_status(log.event_type, log.is_verified)

        # Generate details with more comprehensive information for export
        details = _generate_export_details(log)

        # Extract IP address
        ip_address = _extract_ip_address(log)

        # Parse confidence score
        confidence_score = _parse_confidence_score(log.confidence_score)

        # Format timestamp for Excel compatibility
        timestamp_iso = log.timestamp.isoformat() + "Z"

        enhanced_log = {
            "id": log.id,
            "timestamp": timestamp_iso,
            "employee_name": f"{log.employee.first_name} {log.employee.last_name}",
            "action_type": action_type,
            "warehouse_name": log.employee.warehouse.name
            if log.employee.warehouse
            else "Unknown Warehouse",
            "ip_address": ip_address,
            "success": success,
            "details": details,
            "confidence_score": confidence_score,
            "access_method": log.access_method or "unknown",
            "device_info": _format_device_info_for_export(log.device_info),
        }

        enhanced_logs.append(enhanced_log)

    return enhanced_logs


def _generate_export_details(log: AccessLog) -> str:
    """Generate comprehensive details for export with additional context"""
    action = _map_event_type_to_action(log.event_type)
    method = log.access_method or "unknown method"

    # If there are custom notes, use them
    if log.notes:
        return log.notes

    # Generate detailed descriptions for export
    base_description = ""

    if action == "clock_in":
        if method == "face_recognition":
            confidence = (
                f" (confidence: {log.confidence_score})" if log.confidence_score else ""
            )
            base_description = f"Successful clock-in via facial recognition{confidence}"
        elif method == "manual":
            base_description = "Manual clock-in by administrator"
        elif method == "card":
            base_description = "Clock-in via access card"
        else:
            base_description = f"Clock-in via {method}"
    elif action == "clock_out":
        if method == "face_recognition":
            confidence = (
                f" (confidence: {log.confidence_score})" if log.confidence_score else ""
            )
            base_description = (
                f"Successful clock-out via facial recognition{confidence}"
            )
        elif method == "manual":
            base_description = "Manual clock-out by administrator"
        elif method == "card":
            base_description = "Clock-out via access card"
        else:
            base_description = f"Clock-out via {method}"
    elif action == "denied":
        if method == "face_recognition":
            confidence = (
                f" (confidence: {log.confidence_score})" if log.confidence_score else ""
            )
            base_description = (
                f"Access denied - Low confidence facial recognition{confidence}"
            )
        else:
            base_description = f"Access denied via {method}"
    else:
        base_description = f"Unknown access event via {method}"

    # Add verification status if manually verified
    if log.is_verified:
        base_description += " [Manually Verified]"

    # Add any additional context from additional_data
    if log.additional_data and isinstance(log.additional_data, dict):
        context_items = []
        if log.additional_data.get("reason"):
            context_items.append(f"Reason: {log.additional_data['reason']}")
        if log.additional_data.get("location"):
            context_items.append(f"Location: {log.additional_data['location']}")
        if context_items:
            base_description += f" | {' | '.join(context_items)}"

    return base_description


def _format_device_info_for_export(device_info: Optional[dict]) -> Optional[str]:
    """Format device info as a readable string for export"""
    if not device_info or not isinstance(device_info, dict):
        return None

    # Extract key information
    info_parts = []

    if device_info.get("camera_id"):
        info_parts.append(f"Camera: {device_info['camera_id']}")

    if device_info.get("device_name"):
        info_parts.append(f"Device: {device_info['device_name']}")

    if device_info.get("resolution"):
        info_parts.append(f"Resolution: {device_info['resolution']}")

    if device_info.get("location"):
        info_parts.append(f"Location: {device_info['location']}")

    # Add any other relevant fields
    for key, value in device_info.items():
        if (
            key
            not in [
                "camera_id",
                "device_name",
                "resolution",
                "location",
                "ip_address",
                "ip",
            ]
            and value
        ):
            info_parts.append(f"{key.replace('_', ' ').title()}: {value}")

    return " | ".join(info_parts) if info_parts else None


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


def get_login_logs(
    db: Session,
    company_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get login logs with optional company filtering
    Note: This is a placeholder implementation as we don't have a specific LoginLog model
    Returns UserLoginLog data for now, but can be extended when LoginLog model is implemented
    """
    query = db.query(UserLoginLog)

    # Note: company_id filtering would need to be implemented via User relationship
    # For now, we'll ignore company_id as UserLoginLog doesn't have direct company relation

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


def generate_excel_export(
    db: Session,
    employee_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 1000,
) -> Tuple[bytes, str]:
    """
    Generate Excel file with enhanced access logs

    Returns:
        Tuple[bytes, str]: (file_content, filename)
    """
    # Get the enhanced data
    logs_data = get_export_excel_enhanced_access_logs(
        db=db,
        employee_id=employee_id,
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    # Convert to DataFrame
    if not logs_data:
        # Create empty DataFrame with headers
        df = pd.DataFrame(
            columns=[
                "ID",
                "Timestamp",
                "Employee Name",
                "Action Type",
                "Warehouse Name",
                "IP Address",
                "Success",
                "Details",
                "Confidence Score",
                "Access Method",
                "Device Info",
            ]
        )
    else:
        # Transform data for Excel
        excel_data = []
        for log in logs_data:
            excel_data.append(
                {
                    "ID": log["id"],
                    "Timestamp": log["timestamp"],
                    "Employee Name": log["employee_name"],
                    "Action Type": log["action_type"],
                    "Warehouse Name": log["warehouse_name"],
                    "IP Address": log["ip_address"],
                    "Success": "Yes" if log["success"] else "No",
                    "Details": log["details"],
                    "Confidence Score": log["confidence_score"]
                    if log["confidence_score"] is not None
                    else "N/A",
                    "Access Method": log["access_method"] or "Unknown",
                    "Device Info": log["device_info"] or "N/A",
                }
            )

        df = pd.DataFrame(excel_data)

    # Create Excel file in memory
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Write main data
        df.to_excel(writer, sheet_name="Access Logs", index=False)

        # Get the worksheet for formatting
        worksheet = writer.sheets["Access Logs"]

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # Add summary sheet if we have data
        if logs_data:
            summary_data = _generate_summary_data(logs_data, start_date, end_date)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

    buffer.seek(0)

    # Generate filename
    date_suffix = ""
    if start_date and end_date:
        date_suffix = f"_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    elif start_date:
        date_suffix = f"_from_{start_date.strftime('%Y%m%d')}"
    elif end_date:
        date_suffix = f"_to_{end_date.strftime('%Y%m%d')}"

    filename = f"access_logs_export{date_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return buffer.getvalue(), filename


def _generate_summary_data(
    logs_data: List[Dict[str, Any]],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> List[Dict[str, Any]]:
    """Generate summary statistics for the Excel export"""
    if not logs_data:
        return []

    # Calculate statistics
    total_logs = len(logs_data)
    successful_logs = sum(1 for log in logs_data if log["success"])
    failed_logs = total_logs - successful_logs

    # Count by action type
    action_counts = {}
    for log in logs_data:
        action = log["action_type"]
        action_counts[action] = action_counts.get(action, 0) + 1

    # Count by access method
    method_counts = {}
    for log in logs_data:
        method = log["access_method"] or "Unknown"
        method_counts[method] = method_counts.get(method, 0) + 1

    # Count by warehouse
    warehouse_counts = {}
    for log in logs_data:
        warehouse = log["warehouse_name"]
        warehouse_counts[warehouse] = warehouse_counts.get(warehouse, 0) + 1

    # Create summary data
    summary = [
        {"Metric": "Total Access Logs", "Value": total_logs},
        {"Metric": "Successful Access", "Value": successful_logs},
        {"Metric": "Failed Access", "Value": failed_logs},
        {
            "Metric": "Success Rate",
            "Value": f"{(successful_logs / total_logs * 100):.1f}%"
            if total_logs > 0
            else "0%",
        },
        {"Metric": "", "Value": ""},  # Empty row
        {"Metric": "ACTION BREAKDOWN", "Value": ""},
    ]

    for action, count in action_counts.items():
        summary.append(
            {"Metric": f"  {action.replace('_', ' ').title()}", "Value": count}
        )

    summary.append({"Metric": "", "Value": ""})  # Empty row
    summary.append({"Metric": "ACCESS METHOD BREAKDOWN", "Value": ""})

    for method, count in method_counts.items():
        summary.append(
            {"Metric": f"  {method.replace('_', ' ').title()}", "Value": count}
        )

    summary.append({"Metric": "", "Value": ""})  # Empty row
    summary.append({"Metric": "WAREHOUSE BREAKDOWN", "Value": ""})

    for warehouse, count in warehouse_counts.items():
        summary.append({"Metric": f"  {warehouse}", "Value": count})

    # Add period information
    summary.append({"Metric": "", "Value": ""})  # Empty row
    summary.append({"Metric": "PERIOD INFORMATION", "Value": ""})

    if start_date and end_date:
        summary.append(
            {
                "Metric": "  Period",
                "Value": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            }
        )
    elif start_date:
        summary.append(
            {"Metric": "  From Date", "Value": start_date.strftime("%Y-%m-%d")}
        )
    elif end_date:
        summary.append({"Metric": "  To Date", "Value": end_date.strftime("%Y-%m-%d")})
    else:
        summary.append({"Metric": "  Period", "Value": "All available data"})

    summary.append(
        {
            "Metric": "  Generated At",
            "Value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    return summary
