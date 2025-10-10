import { Component, OnInit } from '@angular/core';
import { ToastController, AlertController } from '@ionic/angular';
import { Preferences } from '@capacitor/preferences';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.page.html',
  styleUrls: ['./configuration.page.scss'],
  imports: [
    FormsModule,
    CommonModule,
    IonicModule,
  ],
})
export class ConfigurationPage implements OnInit {

  config = {
    apiUrl: 'http://localhost:8081',
    cameraQuality: 'medium',
    autoCapture: false,
    captureDelay: 3,
    darkMode: false,
    language: 'en',
    autoLogoutTime: 30,
    biometricLogin: false
  };

  connectionStatus = 'unknown';
  testing = false;
  saving = false;

  constructor(
    private toastController: ToastController,
    private alertController: AlertController,
    private apiService: ApiService
  ) { }

  ngOnInit() {
    this.loadConfiguration();
    this.testConnection();
  }

  /**
   * Load configuration from storage
   */
  async loadConfiguration() {
    try {
      const storedConfig = await Preferences.get({ key: 'app_config' });
      if (storedConfig.value) {
        this.config = { ...this.config, ...JSON.parse(storedConfig.value) };
      }
    } catch (error) {
      console.error('Error loading configuration:', error);
    }
  }

  /**
   * Test API connection
   */
  async testConnection() {
    this.testing = true;
    try {
      // Try to make a simple request to the API
      const response = await fetch(`${this.config.apiUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        this.connectionStatus = 'connected';
        this.showToast('Connection successful', 'success');
      } else {
        this.connectionStatus = 'error';
        this.showToast('Connection failed', 'danger');
      }
    } catch (error) {
      this.connectionStatus = 'disconnected';
      this.showToast('Cannot connect to server', 'danger');
    } finally {
      this.testing = false;
    }
  }

  /**
   * Toggle dark mode
   */
  toggleDarkMode() {
    document.body.classList.toggle('dark', this.config.darkMode);
  }

  /**
   * Save configuration
   */
  async saveConfiguration() {
    this.saving = true;
    try {
      await Preferences.set({
        key: 'app_config',
        value: JSON.stringify(this.config)
      });

      this.showToast('Configuration saved successfully', 'success');
    } catch (error) {
      console.error('Error saving configuration:', error);
      this.showToast('Error saving configuration', 'danger');
    } finally {
      this.saving = false;
    }
  }

  /**
   * Reset to default configuration
   */
  async resetToDefaults() {
    const alert = await this.alertController.create({
      header: 'Reset Configuration',
      message: 'Are you sure you want to reset all settings to default values?',
      buttons: [
        {
          text: 'Cancel',
          role: 'cancel'
        },
        {
          text: 'Reset',
          role: 'destructive',
          handler: async () => {
            this.config = {
              apiUrl: 'http://localhost:8081',
              cameraQuality: 'medium',
              autoCapture: false,
              captureDelay: 3,
              darkMode: false,
              language: 'en',
              autoLogoutTime: 30,
              biometricLogin: false
            };

            await this.saveConfiguration();
            this.showToast('Configuration reset to defaults', 'success');
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
}
