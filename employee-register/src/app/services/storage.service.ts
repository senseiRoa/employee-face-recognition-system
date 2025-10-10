import { Injectable } from '@angular/core';
import { Preferences } from '@capacitor/preferences';

@Injectable({
  providedIn: 'root'
})
export class StorageService {

  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_DATA_KEY = 'user_data';
  private readonly DEVICE_INFO_KEY = 'device_info';

  constructor() { }

  /**
   * Store access token
   * @param token - JWT access token
   */
  async setAccessToken(token: string): Promise<void> {
    await Preferences.set({
      key: this.ACCESS_TOKEN_KEY,
      value: token
    });
  }

  /**
   * Get access token
   * @returns Promise<string | null>
   */
  async getAccessToken(): Promise<string | null> {
    const result = await Preferences.get({ key: this.ACCESS_TOKEN_KEY });
    return result.value;
  }

  /**
   * Store refresh token
   * @param token - Refresh token
   */
  async setRefreshToken(token: string): Promise<void> {
    await Preferences.set({
      key: this.REFRESH_TOKEN_KEY,
      value: token
    });
  }

  /**
   * Get refresh token
   * @returns Promise<string | null>
   */
  async getRefreshToken(): Promise<string | null> {
    const result = await Preferences.get({ key: this.REFRESH_TOKEN_KEY });
    return result.value;
  }

  /**
   * Store user data
   * @param userData - User information object
   */
  async setUserData(userData: any): Promise<void> {
    await Preferences.set({
      key: this.USER_DATA_KEY,
      value: JSON.stringify(userData)
    });
  }

  /**
   * Get user data
   * @returns Promise<any | null>
   */
  async getUserData(): Promise<any | null> {
    const result = await Preferences.get({ key: this.USER_DATA_KEY });
    return result.value ? JSON.parse(result.value) : null;
  }

  /**
   * Store device information
   * @param deviceInfo - Device information object
   */
  async setDeviceInfo(deviceInfo: any): Promise<void> {
    await Preferences.set({
      key: this.DEVICE_INFO_KEY,
      value: JSON.stringify(deviceInfo)
    });
  }

  /**
   * Get device information
   * @returns Promise<any | null>
   */
  async getDeviceInfo(): Promise<any | null> {
    const result = await Preferences.get({ key: this.DEVICE_INFO_KEY });
    return result.value ? JSON.parse(result.value) : null;
  }

  /**
   * Clear all stored data (for logout)
   */
  async clearAll(): Promise<void> {
    await Promise.all([
      Preferences.remove({ key: this.ACCESS_TOKEN_KEY }),
      Preferences.remove({ key: this.REFRESH_TOKEN_KEY }),
      Preferences.remove({ key: this.USER_DATA_KEY }),
      Preferences.remove({ key: this.DEVICE_INFO_KEY })
    ]);
  }

  /**
   * Check if user is authenticated
   * @returns Promise<boolean>
   */
  async isAuthenticated(): Promise<boolean> {
    const accessToken = await this.getAccessToken();
    const refreshToken = await this.getRefreshToken();
    return !!(accessToken && refreshToken);
  }
}
