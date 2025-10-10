export interface Employee {
  id: number;
  warehouse_id: number;
  first_name: string;
  last_name: string;
  email: string;
  created_at: string;
  has_face: boolean;
  is_active: boolean;
}

export interface CreateEmployeeRequest {
  warehouse_id: number;
  first_name: string;
  last_name: string;
  email: string;
  is_active: boolean;
  record_timezone: string;
}

export interface RegisterFaceRequest {
  employee_id: number;
  warehouse_id: number;
  first_name: string;
  last_name: string;
  email: string;
  image_base64: string;
}

export interface RegisterFaceResponse {
  status: string;
  employee_id: number;
  employee_name: string;
}

export interface ClockInOutRequest {
  image_base64: string;
  warehouse_id: number;
  device_timezone: string;
}

export interface CheckInRequest {
  employee_id: number;
  check_type: 'check_in' | 'check_out' | 'break_start' | 'break_end';
  photo_base64: string;
  location: string;
  notes?: string;
}

export interface CheckInResponse {
  success: boolean;
  message: string;
  check_type: string;
  timestamp: string;
  employee_name: string;
}

export interface Warehouse {
  id: number;
  company_id: number;
  name: string;
  location: string;
  created_at: string;
  is_active: boolean;
}
