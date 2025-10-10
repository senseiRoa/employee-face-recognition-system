import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, throwError } from 'rxjs';
import { catchError, tap, switchMap } from 'rxjs/operators';
import { Preferences } from '@capacitor/preferences';
import { ApiService } from './api.service';
import { 
  LoginRequest, 
  LoginResponse, 
  RefreshTokenRequest, 
  User 
} from '../models/auth.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  private isLoggedInSubject = new BehaviorSubject<boolean>(false);
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpirationTime: number | null = null;

  public currentUser$ = this.currentUserSubject.asObservable();
  public isLoggedIn$ = this.isLoggedInSubject.asObservable();

  constructor(private apiService: ApiService) {
    this.initializeAuth();
  }

  /**
   * Initialize authentication state from stored tokens
   */
  private async initializeAuth(): Promise<void> {
    try {
      const storedAccessToken = await Preferences.get({ key: 'access_token' });
      const storedRefreshToken = await Preferences.get({ key: 'refresh_token' });
      const storedUser = await Preferences.get({ key: 'user' });
      const storedExpiration = await Preferences.get({ key: 'token_expiration' });

      if (storedAccessToken.value && storedRefreshToken.value && storedUser.value) {
        this.accessToken = storedAccessToken.value;
        this.refreshToken = storedRefreshToken.value;
        this.tokenExpirationTime = storedExpiration.value ? parseInt(storedExpiration.value) : null;

        const user = JSON.parse(storedUser.value) as User;
        this.currentUserSubject.next(user);

        // Check if token is expired and refresh if needed
        if (this.isTokenExpired()) {
          await this.refreshAccessToken();
        } else {
          this.isLoggedInSubject.next(true);
        }
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      await this.clearStoredAuth();
    }
  }

  /**
   * Login with username/email and password
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.apiService.login(credentials).pipe(
      tap(async (response) => {
        await this.storeAuthData(response);
        this.currentUserSubject.next(response.user);
        this.isLoggedInSubject.next(true);
      }),
      catchError((error) => {
        console.error('Login error:', error);
        return throwError(() => error);
      })
    );
  }

  /**
   * Logout and clear stored authentication data
   */
  async logout(): Promise<void> {
    try {
      if (this.refreshToken) {
        // Call logout endpoint to invalidate refresh token
        await this.apiService.logout({ refresh_token: this.refreshToken }).toPromise();
      }
    } catch (error) {
      console.error('Error during logout API call:', error);
    } finally {
      await this.clearStoredAuth();
      this.currentUserSubject.next(null);
      this.isLoggedInSubject.next(false);
    }
  }

  /**
   * Get current access token, refreshing if necessary
   */
  async getValidAccessToken(): Promise<string | null> {
    if (!this.accessToken || !this.refreshToken) {
      return null;
    }

    if (this.isTokenExpired()) {
      try {
        await this.refreshAccessToken();
      } catch (error) {
        console.error('Token refresh failed:', error);
        await this.logout();
        return null;
      }
    }

    return this.accessToken;
  }

  /**
   * Check if current token is expired
   */
  private isTokenExpired(): boolean {
    if (!this.tokenExpirationTime) {
      return true;
    }
    
    // Add 30 second buffer before expiration
    const bufferTime = 30 * 1000; 
    return Date.now() >= (this.tokenExpirationTime - bufferTime);
  }

  /**
   * Refresh access token using refresh token
   */
  private async refreshAccessToken(): Promise<void> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const refreshRequest: RefreshTokenRequest = { refresh_token: this.refreshToken };
      const response = await this.apiService.refreshToken(refreshRequest).toPromise();
      
      if (response) {
        // Update tokens
        this.accessToken = response.access_token;
        this.refreshToken = response.refresh_token;
        this.tokenExpirationTime = Date.now() + (response.expires_in * 1000);

        // Store new tokens
        await Promise.all([
          Preferences.set({ key: 'access_token', value: this.accessToken }),
          Preferences.set({ key: 'refresh_token', value: this.refreshToken }),
          Preferences.set({ key: 'token_expiration', value: this.tokenExpirationTime.toString() })
        ]);

        this.isLoggedInSubject.next(true);
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw error;
    }
  }

  /**
   * Store authentication data securely
   */
  private async storeAuthData(response: LoginResponse): Promise<void> {
    this.accessToken = response.access_token;
    this.refreshToken = response.refresh_token;
    this.tokenExpirationTime = Date.now() + (response.expires_in * 1000);

    await Promise.all([
      Preferences.set({ key: 'access_token', value: response.access_token }),
      Preferences.set({ key: 'refresh_token', value: response.refresh_token }),
      Preferences.set({ key: 'user', value: JSON.stringify(response.user) }),
      Preferences.set({ key: 'token_expiration', value: this.tokenExpirationTime.toString() })
    ]);
  }

  /**
   * Clear all stored authentication data
   */
  private async clearStoredAuth(): Promise<void> {
    this.accessToken = null;
    this.refreshToken = null;
    this.tokenExpirationTime = null;

    await Promise.all([
      Preferences.remove({ key: 'access_token' }),
      Preferences.remove({ key: 'refresh_token' }),
      Preferences.remove({ key: 'user' }),
      Preferences.remove({ key: 'token_expiration' })
    ]);
  }

  /**
   * Get current user data
   */
  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  /**
   * Check if user is currently logged in
   */
  isAuthenticated(): boolean {
    return this.isLoggedInSubject.value;
  }
}