import { Component, OnInit } from '@angular/core';
import { ToastController } from '@ionic/angular';
// import { Device } from '@capacitor/device';
import { App } from '@capacitor/app';
// import { Network } from '@capacitor/network';
import { Camera, CameraResultType } from '@capacitor/camera';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';

@Component({
  selector: 'app-device-details',
  templateUrl: './device-details.page.html',
  styleUrls: ['./device-details.page.scss'],
  imports: [
    FormsModule,
    CommonModule,
    IonicModule,
  ],
})
export class DeviceDetailsPage implements OnInit {

  deviceInfo = {
    model: '',
    platform: '',
    operatingSystem: '',
    osVersion: '',
    deviceId: ''
  };

  appInfo = {
    name: 'Employee Register',
    version: '1.0.0',
    build: '1',
    id: 'com.company.employee-register'
  };

  networkInfo = {
    connected: false,
    connectionType: ''
  };

  cameraInfo = {
    available: false,
    frontCamera: false,
    rearCamera: false
  };

  storageInfo = {
    available: 'Calculating...',
    used: 'Calculating...',
    total: 'Calculating...'
  };

  permissions = [
    {
      name: 'camera',
      displayName: 'Camera Access',
      description: 'Required for face recognition',
      granted: false
    },
    {
      name: 'storage',
      displayName: 'Storage Access',
      description: 'Required for caching data',
      granted: false
    },
    {
      name: 'network',
      displayName: 'Network Access',
      description: 'Required for API communication',
      granted: false
    }
  ];

  testingCamera = false;
  checkingPermissions = false;

  constructor(
    private toastController: ToastController
  ) { }

  ngOnInit() {
    this.loadDeviceInfo();
    this.loadAppInfo();
    this.loadNetworkInfo();
    this.loadCameraInfo();
    this.loadStorageInfo();
    this.checkPermissions();
  }

  /**
   * Load device information
   */
  async loadDeviceInfo() {
    try {
      // Mock device info for now - replace with actual Device.getInfo() when capacitor plugins are installed
      this.deviceInfo = {
        model: 'Mock Device',
        platform: 'web',
        operatingSystem: 'web',
        osVersion: '1.0',
        deviceId: await this.getDeviceId()
      };
    } catch (error) {
      console.error('Error loading device info:', error);
    }
  }

  /**
   * Get unique device ID
   */
  async getDeviceId(): Promise<string> {
    try {
      // Mock device ID for now
      return 'device_' + Math.random().toString(36).substring(2, 15);
    } catch (error) {
      return 'device_' + Math.random().toString(36).substring(2, 15);
    }
  }

  /**
   * Load app information
   */
  async loadAppInfo() {
    try {
      const info = await App.getInfo();
      this.appInfo = {
        name: info.name,
        version: info.version,
        build: info.build,
        id: info.id
      };
    } catch (error) {
      console.error('Error loading app info:', error);
    }
  }

  /**
   * Load network information
   */
  async loadNetworkInfo() {
    try {
      // Mock network info for now - replace with actual Network.getStatus() when capacitor plugins are installed
      this.networkInfo = {
        connected: navigator.onLine,
        connectionType: 'wifi'
      };

      // Listen for network changes
      window.addEventListener('online', () => {
        this.networkInfo.connected = true;
      });

      window.addEventListener('offline', () => {
        this.networkInfo.connected = false;
      });
    } catch (error) {
      console.error('Error loading network info:', error);
    }
  }

  /**
   * Load camera information
   */
  async loadCameraInfo() {
    try {
      // Check camera permissions to determine availability
      const permissions = await Camera.checkPermissions();
      this.cameraInfo.available = permissions.camera === 'granted';

      // For simplicity, assume both cameras are available if permission is granted
      if (this.cameraInfo.available) {
        this.cameraInfo.frontCamera = true;
        this.cameraInfo.rearCamera = true;
      }
    } catch (error) {
      console.error('Error loading camera info:', error);
      this.cameraInfo.available = false;
    }
  }

  /**
   * Load storage information
   */
  async loadStorageInfo() {
    try {
      // This is a simplified storage info - in a real app you might use File system API
      this.storageInfo = {
        available: '2.5 GB',
        used: '1.2 GB',
        total: '8.0 GB'
      };
    } catch (error) {
      console.error('Error loading storage info:', error);
    }
  }

  /**
   * Test camera functionality
   */
  async testCamera() {
    this.testingCamera = true;
    try {
      const image = await Camera.getPhoto({
        quality: 50,
        allowEditing: false,
        resultType: CameraResultType.Uri
      });

      if (image) {
        this.showToast('Camera test successful!', 'success');
      }
    } catch (error) {
      console.error('Camera test failed:', error);
      this.showToast('Camera test failed. Please check permissions.', 'danger');
    } finally {
      this.testingCamera = false;
    }
  }

  /**
   * Check app permissions
   */
  async checkPermissions() {
    this.checkingPermissions = true;
    try {
      // Check camera permission
      const cameraPermissions = await Camera.checkPermissions();
      this.permissions[0].granted = cameraPermissions.camera === 'granted';

      // Update camera info based on permissions
      this.cameraInfo.available = this.permissions[0].granted;

      // For storage and network, we'll assume they're granted in a web/hybrid context
      this.permissions[1].granted = true; // Storage
      this.permissions[2].granted = this.networkInfo.connected; // Network

    } catch (error) {
      console.error('Error checking permissions:', error);
    } finally {
      this.checkingPermissions = false;
    }
  }

  /**
   * Get icon for permission type
   */
  getPermissionIcon(permissionName: string): string {
    switch (permissionName) {
      case 'camera': return 'camera-outline';
      case 'storage': return 'folder-outline';
      case 'network': return 'wifi-outline';
      default: return 'shield-outline';
    }
  }

  /**
   * Refresh all device information
   */
  async refreshDeviceInfo() {
    await Promise.all([
      this.loadDeviceInfo(),
      this.loadAppInfo(),
      this.loadNetworkInfo(),
      this.loadCameraInfo(),
      this.loadStorageInfo(),
      this.checkPermissions()
    ]);

    this.showToast('Device information refreshed', 'success');
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
