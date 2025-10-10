import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { environment } from "../../environments/environment";
import {
  LoginRequest,
  LoginResponse,
  RefreshTokenRequest,
  RefreshTokenResponse,
  LogoutRequest,
  LogoutResponse
} from "../models/auth.model";
import {
  CreateEmployeeRequest,
  Employee,
  RegisterFaceRequest,
  RegisterFaceResponse,
  ClockInOutRequest,
  Warehouse
} from "../models/employee.model";
import { AccessLog, AccessLogParams } from "../models/reports.model";

@Injectable({ providedIn: "root" })
export class ApiService {
  private baseUrl = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  /**
   * Get UTC offset format (e.g., "UTC-5", "UTC+3")
   * @returns {string} UTC offset string
   */
  private getTimezoneOffset(): string {
    try {
      const offset = new Date().getTimezoneOffset();
      const hours = Math.abs(Math.floor(offset / 60));
      const sign = offset > 0 ? '-' : '+';

      return `UTC${sign}${hours}`;
    } catch (error) {
      console.warn('Could not calculate timezone offset, using UTC:', error);
      return 'UTC';
    }
  }

  /**
   * Get authorization headers with bearer token
   */
  private getAuthHeaders(token: string): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  /**
   * Get standard headers without authorization
   */
  private getHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Content-Type': 'application/json'
    });
  }

  // ========== Authentication Endpoints ==========

  /**
   * Login with username/email and password
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    const loginData = {
      ...credentials,
      client_timezone: this.getTimezoneOffset(),
      device_info: navigator.userAgent || ""
    };

    return this.http.post<LoginResponse>(`${this.baseUrl}/auth/login`, loginData, {
      headers: this.getHeaders()
    });
  }

  /**
   * Refresh access token using refresh token
   */
  refreshToken(request: RefreshTokenRequest): Observable<RefreshTokenResponse> {
    return this.http.post<RefreshTokenResponse>(`${this.baseUrl}/auth/refresh`, request, {
      headers: this.getHeaders()
    });
  }

  /**
   * Logout and invalidate refresh token
   */
  logout(request: LogoutRequest): Observable<LogoutResponse> {
    return this.http.post<LogoutResponse>(`${this.baseUrl}/auth/logout`, request, {
      headers: this.getHeaders()
    });
  }

  // ========== Warehouse Endpoints ==========

  /**
   * Get warehouses for a company
   */
  getWarehouses(companyId: number, skip: number = 0, limit: number = 100, token: string): Observable<Warehouse[]> {
    return this.http.get<Warehouse[]>(`${this.baseUrl}/warehouses/?company_id=${companyId}&skip=${skip}&limit=${limit}`, {
      headers: this.getAuthHeaders(token)
    });
  }

  // ========== Employee Endpoints ==========

  /**
   * Create a new employee
   */
  createEmployee(employee: CreateEmployeeRequest, token: string): Observable<Employee> {
    return this.http.post<Employee>(`${this.baseUrl}/employees/`, employee, {
      headers: this.getAuthHeaders(token)
    });
  }

  /**
   * Register face for an employee
   */
  registerFace(request: RegisterFaceRequest, token: string): Observable<RegisterFaceResponse> {
    // Log the request for debugging (hide the actual base64 content)
    console.log('API Service - registerFace request:', {
      ...request,
      image_base64: `[base64 string length: ${request.image_base64?.length || 0}]`
    });
    
    return this.http.post<RegisterFaceResponse>(`${this.baseUrl}/employees/register_face`, request, {
      headers: this.getAuthHeaders(token)
    });
  }

  /**
   * Clock in/out using face recognition
   */
  clockInOut(request: ClockInOutRequest, token: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/employees/clock_in_out`, request, {
      headers: this.getAuthHeaders(token)
    });
  }

  // ========== Reports Endpoints ==========

  /**
   * Get access logs with optional filters
   */
  getAccessLogs(params: AccessLogParams, token: string): Observable<AccessLog[]> {
    let queryParams = new URLSearchParams();

    if (params.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);

    return this.http.get<AccessLog[]>(`${this.baseUrl}/logs/access?${queryParams.toString()}`, {
      headers: this.getAuthHeaders(token)
    });
  }
}
