import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { LoadingController, AlertController, ToastController } from '@ionic/angular';
import { AuthService } from '../services/auth.service';
import { LoginRequest } from '../models/auth.model';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';

@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  imports: [
    FormsModule,
    CommonModule,
    IonicModule,
  ],
})
export class LoginPage implements OnInit {

  loginData: LoginRequest = {
    username_or_email: '',
    password: '',
    client_timezone: 'UTC-5',
    device_info: ''
  };

  showPassword = false;
  isLoading = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private loadingController: LoadingController,
    private alertController: AlertController,
    private toastController: ToastController
  ) { }

  ngOnInit() {
    this.checkAuthentication();
    this.setDeviceInfo();
  }

  /**
   * Check if user is already authenticated
   */
  async checkAuthentication() {
    const isAuthenticated = await this.authService.isAuthenticated();
    if (isAuthenticated) {
      this.router.navigate(['/home'], { replaceUrl: true });
    }
  }

  /**
   * Set device information
   */
  setDeviceInfo() {
    this.loginData.device_info = navigator.userAgent;
  }

  /**
   * Toggle password visibility
   */
  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  /**
   * Handle login form submission
   */
  async onLogin() {
    if (!this.validateForm()) {
      return;
    }

    const loading = await this.loadingController.create({
      message: 'Signing in...',
      spinner: 'crescent'
    });
    await loading.present();

    try {
      this.isLoading = true;
      this.authService.login(this.loginData).subscribe({
        next: async (response) => {
          if (response.access_token) {
            await this.showSuccessToast('Login successful');
            this.router.navigate(['/home'], { replaceUrl: true });
          }
        },
        error: async (error: any) => {
          console.error('Login error:', error);
          let errorMessage = 'Invalid credentials. Please check your username/email and password.';
          
          // Handle specific HTTP error responses
          if (error.status === 401) {
            if (error.error && error.error.detail) {
              errorMessage = error.error.detail;
            } else {
              errorMessage = 'Incorrect username/email or password';
            }
          } else if (error.status === 400) {
            errorMessage = 'Invalid request. Please check your input.';
          } else if (error.status === 500) {
            errorMessage = 'Server error. Please try again later.';
          } else if (error.status === 0) {
            errorMessage = 'Cannot connect to server. Please check your internet connection.';
          }
          
          await this.showErrorAlert('Login Failed', errorMessage);
        },
        complete: async () => {
          this.isLoading = false;
          await loading.dismiss();
        }
      });
    } catch (error: any) {
      console.error('Login error:', error);
      await this.showErrorAlert('Login Failed', 'An unexpected error occurred. Please try again.');
      this.isLoading = false;
      await loading.dismiss();
    }
  }

  /**
   * Validate login form
   */
  validateForm(): boolean {
    if (!this.loginData.username_or_email.trim()) {
      this.showErrorAlert('Validation Error', 'Please enter your username or email');
      return false;
    }

    if (!this.loginData.password.trim()) {
      this.showErrorAlert('Validation Error', 'Please enter your password');
      return false;
    }

    if (this.loginData.password.length < 6) {
      this.showErrorAlert('Validation Error', 'Password must be at least 6 characters');
      return false;
    }

    return true;
  }

  /**
   * Show error alert
   */
  async showErrorAlert(header: string, message: string) {
    const alert = await this.alertController.create({
      header,
      message,
      buttons: ['OK']
    });
    await alert.present();
  }

  /**
   * Show success toast
   */
  async showSuccessToast(message: string) {
    const toast = await this.toastController.create({
      message,
      duration: 2000,
      position: 'top',
      color: 'success'
    });
    await toast.present();
  }
}
