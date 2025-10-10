import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ToastController, AlertController, ActionSheetController } from '@ionic/angular';
import { AuthService } from '../services/auth.service';
import { CameraService } from '../services/camera.service';
import { ApiService } from '../services/api.service';
import { CreateEmployeeRequest, RegisterFaceRequest, ClockInOutRequest } from '../models/employee.model';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-time-tracker',
  templateUrl: './time-tracker.page.html',
  styleUrls: ['./time-tracker.page.scss'],
  imports: [
    FormsModule,
    CommonModule,
    IonicModule,
  ],
})
export class TimeTrackerPage implements OnInit {

  currentView: 'register' | 'checkin' = 'checkin';

  // Employee Registration
  newEmployee: CreateEmployeeRequest = {
    warehouse_id: 1, // Default warehouse ID
    first_name: '',
    last_name: '',
    email: '',
    is_active: true,
    record_timezone: 'GMT+00:00' // Will be updated in ngOnInit
  };

  // Check-in/out
  isLoading = false;
  currentUser: any = null;
  lastAction: string | null = null;
  lastActionTime: Date | null = null;

  constructor(
    private authService: AuthService,
    private cameraService: CameraService,
    private apiService: ApiService,
    private router: Router,
    private toastController: ToastController,
    private alertController: AlertController,
    private actionSheetController: ActionSheetController
  ) { }

  ngOnInit() {
    this.loadCurrentUser();
    // Update timezone in employee object
    this.newEmployee.record_timezone = this.getGMTOffset();
  }

  ionViewWillEnter() {
    this.loadCurrentUser();
  }

  /**
   * Load current user data
   */
  async loadCurrentUser() {
    try {
      this.currentUser = await this.authService.getCurrentUser();
    } catch (error) {
      console.error('Error loading user:', error);
    }
  }

  /**
   * Switch between register and check-in views
   */
  switchView(view: 'register' | 'checkin') {
    this.currentView = view;
  }

  /**
   * Register new employee with face
   */
  async registerEmployee() {
    if (!this.validateEmployeeForm()) {
      return;
    }

    this.isLoading = true;
    try {
      // Take photo first (get only base64 string for backend)
      const photo = await this.cameraService.takePhotoBase64Only();
      if (!photo) {
        this.showToast('Photo is required for registration', 'danger');
        return;
      }

      // Get auth token
      const token = await this.authService.getValidAccessToken();
      if (!token) {
        this.showToast('Authentication required', 'danger');
        return;
      }

      // Create employee
      const createEmployeeResponse = await firstValueFrom(this.apiService.createEmployee(this.newEmployee, token));

      if (createEmployeeResponse?.id) {
        // Register face
        const faceData = {
          employee_id: createEmployeeResponse.id,
          warehouse_id: this.newEmployee.warehouse_id,
          first_name: this.newEmployee.first_name,
          last_name: this.newEmployee.last_name,
          email: this.newEmployee.email,
          image_base64: photo
        };

        console.log('Sending face registration data:', {
          ...faceData,
          image_base64: `[base64 string length: ${photo.length}]`
        });

        await firstValueFrom(this.apiService.registerFace(faceData, token));

        this.showToast('Employee registered successfully!', 'success');
        this.resetEmployeeForm();
      }
    } catch (error) {
      console.error('Registration error:', error);
      this.showToast('Registration failed. Please try again.', 'danger');
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Validate employee registration form
   */
  validateEmployeeForm(): boolean {
    if (!this.newEmployee.first_name || !this.newEmployee.last_name) {
      this.showToast('First name and last name are required', 'danger');
      return false;
    }

    if (!this.newEmployee.email) {
      this.showToast('Email is required', 'danger');
      return false;
    }

    return true;
  }

  /**
   * Reset employee registration form
   */
  resetEmployeeForm() {
    this.newEmployee = {
      warehouse_id: 1,
      first_name: '',
      last_name: '',
      email: '',
      is_active: true,
      record_timezone: this.getGMTOffset()
    };
  }

  /**
   * Show clock-in/out options
   */
  async showClockOptions() {
    const actionSheet = await this.actionSheetController.create({
      header: 'Time Tracking Options',
      buttons: [
        {
          text: 'Clock In',
          icon: 'log-in-outline',
          handler: () => {
            this.performClockAction('clock_in');
          }
        },
        {
          text: 'Clock Out',
          icon: 'log-out-outline',
          handler: () => {
            this.performClockAction('clock_out');
          }
        },
        {
          text: 'Break Start',
          icon: 'cafe-outline',
          handler: () => {
            this.performClockAction('break_start');
          }
        },
        {
          text: 'Break End',
          icon: 'checkmark-circle-outline',
          handler: () => {
            this.performClockAction('break_end');
          }
        },
        {
          text: 'Cancel',
          icon: 'close',
          role: 'cancel'
        }
      ]
    });
    await actionSheet.present();
  }

  /**
   * Perform clock action with face recognition
   */
  async performClockAction(action: 'clock_in' | 'clock_out' | 'break_start' | 'break_end') {
    this.isLoading = true;
    try {
      // Take photo for face recognition (get only base64 string for backend)
      const photo = await this.cameraService.takePhotoBase64Only();
      if (!photo) {
        this.showToast('Photo is required for time tracking', 'danger');
        return;
      }

      // Get auth token
      const token = await this.authService.getValidAccessToken();
      if (!token) {
        this.showToast('Authentication required', 'danger');
        return;
      }

      // Prepare clock data
      const clockData = {
        image_base64: photo,
        warehouse_id: 1, // Default warehouse ID
        device_timezone: this.getGMTOffset()
      };

      console.log('Sending clock data:', {
        ...clockData,
        image_base64: `[base64 string length: ${photo.length}]`
      });

      // Send to API
      const response = await firstValueFrom(this.apiService.clockInOut(clockData, token));

      console.log('Clock in/out response:', response);

      this.lastAction = this.getActionDisplayText(action);
      this.lastActionTime = new Date();

      this.showToast(`${this.lastAction} successful!`, 'success');
    } catch (error) {
      console.error('Clock action error:', error);
      this.showToast('Action failed. Please try again.', 'danger');
    } finally {
      this.isLoading = false;
    }
  }

  /**
   * Get display text for action type
   */
  getActionDisplayText(action: string): string {
    switch (action) {
      case 'clock_in': return 'Clock In';
      case 'clock_out': return 'Clock Out';
      case 'break_start': return 'Break Start';
      case 'break_end': return 'Break End';
      default: return action;
    }
  }

  /**
   * Get GMT offset in the format GMT-XX or GMT+XX
   */
  getGMTOffset(): string {
    const now = new Date();
    const offset = now.getTimezoneOffset();
    const hours = Math.floor(Math.abs(offset) / 60);
    const minutes = Math.abs(offset) % 60;
    const sign = offset > 0 ? '-' : '+';
    
    return `GMT${sign}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  }

  /**
   * Navigate to reports
   */
  goToReports() {
    this.router.navigate(['/reports']);
  }

  /**
   * Show toast message
   */
  async showToast(message: string, color: 'success' | 'danger' | 'warning' = 'success') {
    const toast = await this.toastController.create({
      message,
      duration: 3000,
      color,
      position: 'bottom'
    });
    await toast.present();
  }
}
