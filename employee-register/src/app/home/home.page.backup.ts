import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController, ActionSheetController, LoadingController, ToastController } from '@ionic/angular';
import { AuthService } from '../services/auth.service';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  imports: [
    FormsModule,
    CommonModule,
    IonicModule,
  ],
})
export class HomePage implements OnInit {

  currentUser: any = null;
  currentDate: Date = new Date();
  loading = false;
  isCheckedIn = false;
  todayHours = '0.0h';
  weekHours = '0.0h';
  lastAction = '';
  lastActionTime: Date | null = null;
  recentActivities: any[] = [];

  constructor(
    private authService: AuthService,
    private apiService: ApiService,
    private router: Router,
    private alertController: AlertController,
    private actionSheetController: ActionSheetController,
    private loadingController: LoadingController,
    private toastController: ToastController
  ) { }

  ngOnInit() {
    this.loadDashboardData();
  }

  ionViewWillEnter() {
    this.loadDashboardData();
  }

  /**
   * Load all dashboard data
   */
  async loadDashboardData() {
    this.loading = true;
    try {
      await Promise.all([
        this.loadUserData(),
        this.loadTimeStats(),
        this.loadRecentActivities(),
        this.loadCurrentStatus()
      ]);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      this.showToast('Error loading dashboard data', 'danger');
    } finally {
      this.loading = false;
    }
  }

  /**
   * Load current user data
   */
  async loadUserData() {
    try {
      this.currentUser = await this.authService.getCurrentUser();
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  }

  /**
   * Load time tracking statistics
   */
  async loadTimeStats() {
    try {
      // TODO: Replace with actual API call
      // For now, using mock data
      this.todayHours = '8.5h';
      this.weekHours = '32.0h';
    } catch (error) {
      console.error('Error loading time stats:', error);
    }
  }

  /**
   * Load recent activity logs
   */
  async loadRecentActivities() {
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7); // Last 7 days

      const formatDate = (date: Date) => date.toISOString().split('T')[0];
      
      const response = await this.apiService.get(
        `/logs/access?skip=0&limit=5&start_date=${formatDate(startDate)}&end_date=${formatDate(endDate)}`
      );
      
      this.recentActivities = response || [];
    } catch (error) {
      console.error('Error loading recent activities:', error);
      this.recentActivities = [];
    }
  }

  /**
   * Load current check-in status
   */
  async loadCurrentStatus() {
    try {
      // TODO: Implement actual status check from backend
      // For now, using mock logic
      if (this.recentActivities.length > 0) {
        const lastActivity = this.recentActivities[0];
        this.isCheckedIn = lastActivity.action_type === 'clock_in';
        this.lastAction = lastActivity.action_type === 'clock_in' ? 'Checked In' : 'Checked Out';
        this.lastActionTime = new Date(lastActivity.timestamp);
      }
    } catch (error) {
      console.error('Error loading current status:', error);
    }
  }

  /**
   * Navigate to Time Tracker module
   */
  navigateToTimeTracker() {
    this.router.navigate(['/time-tracker']);
  }

  /**
   * Navigate to Reports module
   */
  navigateToReports() {
    this.router.navigate(['/reports']);
  }

  /**
   * Show user profile options
   */
  async showProfile() {
    const actionSheet = await this.actionSheetController.create({
      header: 'Profile Options',
      buttons: [
        {
          text: 'View Profile',
          icon: 'person-outline',
          handler: () => {
            this.viewProfile();
          }
        },
        {
          text: 'Settings',
          icon: 'settings-outline',
          handler: () => {
            this.router.navigate(['/configuration']);
          }
        },
        {
          text: 'Logout',
          icon: 'log-out-outline',
          role: 'destructive',
          handler: () => {
            this.logout();
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
   * View user profile
   */
  async viewProfile() {
    const alert = await this.alertController.create({
      header: 'User Profile',
      message: `
        <strong>Name:</strong> ${this.currentUser?.first_name} ${this.currentUser?.last_name}<br>
        <strong>Email:</strong> ${this.currentUser?.email}<br>
        <strong>Role:</strong> ${this.currentUser?.role}<br>
        <strong>Warehouse:</strong> ${this.currentUser?.warehouse_name}
      `,
      buttons: ['OK']
    });
    await alert.present();
  }

  /**
   * Logout user
   */
  async logout() {
    const alert = await this.alertController.create({
      header: 'Confirm Logout',
      message: 'Are you sure you want to logout?',
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel'
        },
        {
          text: 'Logout',
          role: 'destructive',
          handler: async () => {
            try {
              await this.authService.logout();
              this.router.navigate(['/login']);
            } catch (error) {
              console.error('Logout error:', error);
              this.showToast('Error logging out', 'danger');
            }
          }
        }
      ]
    });
    await alert.present();
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

  /**
   * Refresh dashboard data
   */
  async refreshData(event?: any) {
    await this.loadDashboardData();
    if (event) {
      event.target.complete();
    }
  }
}
    this.loadStats();
    this.loadLastCheckIn();
  }

  /**
   * Load user data
   */
  async loadUserData() {
    try {
      this.user = await this.authService.getCurrentUser();
    } catch (error) {
      console.error('Error loading user data:', error);
    }
  }

  /**
   * Load user statistics
   */
  async loadStats() {
    try {
      // Mock data for now - replace with actual API calls
      this.stats = {
        totalHours: 160.5,
        weeklyHours: 40,
        monthlyHours: 160.5
      };
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  }

  /**
   * Load last check-in information
   */
  async loadLastCheckIn() {
    try {
      // Mock data for now - replace with actual API call
      this.lastCheckIn = {
        type: 'Check In',
        timestamp: new Date(),
        location: 'Office'
      };
    } catch (error) {
      console.error('Error loading last check-in:', error);
    }
  }

  /**
   * Handle check-in/check-out action
   */
  async presentCheckInOptions() {
    const actionSheet = await this.actionSheetController.create({
      header: 'Time Tracking',
      buttons: [
        {
          text: 'Check In',
          icon: 'log-in-outline',
          handler: () => {
            this.performCheckIn('check_in');
          }
        },
        {
          text: 'Check Out',
          icon: 'log-out-outline',
          handler: () => {
            this.performCheckIn('check_out');
          }
        },
        {
          text: 'Break Start',
          icon: 'pause-outline',
          handler: () => {
            this.performCheckIn('break_start');
          }
        },
        {
          text: 'Break End',
          icon: 'play-outline',
          handler: () => {
            this.performCheckIn('break_end');
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
   * Perform check-in with face recognition
   */
  async performCheckIn(type: 'check_in' | 'check_out' | 'break_start' | 'break_end') {
    const loading = await this.loadingController.create({
      message: 'Processing...',
      spinner: 'crescent'
    });
    await loading.present();

    try {
      // Check camera availability
      const cameraAvailable = await this.cameraService.isCameraAvailable();
      if (!cameraAvailable) {
        throw new Error('Camera not available');
      }

      // Capture photo
      const photoBase64 = await this.cameraService.capturePhoto();

      // Validate image
      const isValidImage = await this.cameraService.validateImage(photoBase64);
      if (!isValidImage) {
        throw new Error('Image quality too low for face recognition');
      }

      // Prepare check-in request
      const checkInData: CheckInRequest = {
        employee_id: this.user?.id || 0,
        check_type: type,
        photo_base64: photoBase64.split(',')[1], // Remove data:image/jpeg;base64, prefix
        location: 'Office', // You can add location detection here
        notes: ''
      };

      // Send check-in request
      this.apiService.checkIn(checkInData).subscribe({
        next: async (response) => {
          await this.showSuccessToast(`${this.getCheckTypeText(type)} successful`);
          this.loadStats();
          this.loadLastCheckIn();
        },
        error: async (error) => {
          console.error('Check-in error:', error);
          await this.showErrorAlert('Check-in Failed', error.message || 'Face recognition failed');
        }
      });

    } catch (error: any) {
      console.error('Check-in error:', error);
      await this.showErrorAlert('Error', error.message || 'Failed to process check-in');
    } finally {
      await loading.dismiss();
    }
  }

  /**
   * Get check type text for display
   */
  getCheckTypeText(type: string): string {
    switch (type) {
      case 'check_in': return 'Check In';
      case 'check_out': return 'Check Out';
      case 'break_start': return 'Break Start';
      case 'break_end': return 'Break End';
      default: return 'Action';
    }
  }

  /**
   * Navigate to reports page
   */
  goToReports() {
    this.router.navigate(['/reports']);
  }

  /**
   * Navigate to profile page
   */
  goToProfile() {
    this.router.navigate(['/profile']);
  }

  /**
   * Logout user
   */
  async logout() {
    const alert = await this.alertController.create({
      header: 'Logout',
      message: 'Are you sure you want to logout?',
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel'
        },
        {
          text: 'Logout',
          handler: async () => {
            await this.authService.logout();
            this.router.navigate(['/login'], { replaceUrl: true });
          }
        }
      ]
    });
    await alert.present();
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
