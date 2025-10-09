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

  /**
   * Get GMT offset format (e.g., "GMT-05", "GMT+03")
   * @returns {string} GMT offset string
   */
  private getGMTOffset(): string {
    try {
      const offset = new Date().getTimezoneOffset();
      const hours = Math.abs(Math.floor(offset / 60));
      const sign = offset > 0 ? '-' : '+';
      
      return `GMT${sign}${hours.toString().padStart(2, '0')}`;
    } catch (error) {
      console.warn('Could not calculate GMT offset, using UTC:', error);
      return 'UTC';
    }
  }

  registerFace(name: string, image_base64: string) {
    // Get device timezone in GMT format
    const deviceTimezone = this.getGMTOffset();
    
    return this.http.post(
      `${this.base}/employees/register_face`,
      { 
        name, 
        image_data: image_base64,  // Updated field name
        device_timezone: deviceTimezone  // NEW: Include device timezone in GMT format
      },
      { headers: this.headers }
    );
  }

  checkInOut(image_base64: string) {
    // Get device timezone in GMT format
    const deviceTimezone = this.getGMTOffset();
    
    return this.http.post(
      `${this.base}/employees/check`,  // Updated endpoint name
      { 
        image_data: image_base64,  // Updated field name
        device_timezone: deviceTimezone  // NEW: Include device timezone in GMT format
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
