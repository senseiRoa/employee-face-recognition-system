import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AlertController, ActionSheetController, LoadingController, ToastController, MenuController, ModalController } from '@ionic/angular';
import { AuthService } from '../services/auth.service';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import {
  personCircleOutline,
  businessOutline,
  timeOutline,
  calendarOutline,
  barChartOutline,
  checkmarkCircle,
  closeCircle,
  logInOutline,
  logOutOutline,
  documentOutline,
  personOutline,
  settingsOutline,
  close
} from 'ionicons/icons';
import { UserProfileModalComponent } from '../components/user-profile-modal/user-profile-modal.component';

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
    private toastController: ToastController,
    private menuController: MenuController,
    private modalController: ModalController
  ) {
    addIcons({
      personCircleOutline,
      businessOutline,
      timeOutline,
      calendarOutline,
      barChartOutline,
      checkmarkCircle,
      closeCircle,
      logInOutline,
      logOutOutline,
      documentOutline,
      personOutline,
      settingsOutline,
      close
    });
  }

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
      const token = await this.authService.getValidAccessToken();
      if (!token) return;

      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7); // Last 7 days

      const params = {
        skip: 0,
        limit: 5,
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0]
      };

      this.apiService.getAccessLogs(params, token).subscribe({
        next: (response) => {
          this.recentActivities = response || [];
          this.loadCurrentStatus(); // Update status after loading activities
        },
        error: (error) => {
          console.error('Error loading recent activities:', error);
          this.recentActivities = [];
        }
      });
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
    const modal = await this.modalController.create({
      component: UserProfileModalComponent,
      componentProps: {
        user: this.currentUser
      },
      presentingElement: undefined,
      showBackdrop: true,
      backdropDismiss: true
    });
    
    await modal.present();
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
