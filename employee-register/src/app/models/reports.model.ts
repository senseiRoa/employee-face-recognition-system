export interface AccessLog {
  id: number;
  timestamp: string;
  employee_name: string;
  action_type: string;
  warehouse_name: string;
  ip_address: string;
  success: boolean;
  details: string;
  confidence_score: number;
  access_method: string;
  device_info: {
    type: string;
    device: string;
  };
}

export interface AccessLogParams {
  skip?: number;
  limit?: number;
  start_date?: string;
  end_date?: string;
}
