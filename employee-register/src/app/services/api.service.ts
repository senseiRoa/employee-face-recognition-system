import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { environment } from "src/environments/environment";

@Injectable({ providedIn: 'root' })
export class ApiService {
  private base = environment.apiBaseUrl;

  constructor(private http: HttpClient) {}

  registerFace(employee_id: string, name: string, image_base64: string) {
    return this.http.post(`${this.base}/register_face`, { employee_id, name, image_base64 });
  }

  checkInOut(image_base64: string) {
    return this.http.post(`${this.base}/check_in_out`, { image_base64 });
  }

  getLogs() {
    return this.http.get(`${this.base}/logs`);
  }
}