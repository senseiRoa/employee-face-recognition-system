import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { environment } from "src/environments/environment";

@Injectable({ providedIn: "root" })
export class ApiService {
  private base = environment.apiBaseUrl;
  token = "sub=user_everglades,exp=1759500992.a_very_insecure_secret_key";
  headers = {};

  constructor(private http: HttpClient) {
    this.headers = { Authorization: `Bearer ${this.token}` };
  }

  registerFace(name: string, image_base64: string) {
    // Get device timezone
    const deviceTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    
    return this.http.post(
      `${this.base}/employees/register_face`,
      { 
        name, 
        image_data: image_base64,  // Updated field name
        device_timezone: deviceTimezone  // NEW: Include device timezone
      },
      { headers: this.headers }
    );
  }

  checkInOut(image_base64: string) {
    // Get device timezone
    const deviceTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
    
    return this.http.post(
      `${this.base}/employees/check`,  // Updated endpoint name
      { 
        image_data: image_base64,  // Updated field name
        device_timezone: deviceTimezone  // NEW: Include device timezone
      },
      { headers: this.headers }
    );
  }

  getLogs() {
    return this.http.get(`${this.base}/employees/logs`, {
      headers: this.headers
    });
  }
}
