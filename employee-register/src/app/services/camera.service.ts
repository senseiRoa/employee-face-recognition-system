import { Injectable } from '@angular/core';
import { Camera, CameraResultType, CameraSource, Photo } from '@capacitor/camera';
import { Platform } from '@ionic/angular';

@Injectable({
  providedIn: 'root'
})
export class CameraService {

  constructor(private platform: Platform) { }

  /**
   * Capture photo using device camera
   * @returns Promise<string> - Base64 encoded image
   */
  async capturePhoto(): Promise<string> {
    try {
      const image: Photo = await Camera.getPhoto({
        quality: 90,
        allowEditing: false,
        resultType: CameraResultType.Base64,
        source: CameraSource.Camera,
        width: 800,
        height: 600,
        correctOrientation: true
      });

      if (image.base64String) {
        return `data:image/jpeg;base64,${image.base64String}`;
      } else {
        throw new Error('Failed to capture image');
      }
    } catch (error) {
      console.error('Error capturing photo:', error);
      throw error;
    }
  }

  /**
   * Check if camera is available on the device
   * @returns boolean
   */
  async isCameraAvailable(): Promise<boolean> {
    try {
      if (this.platform.is('hybrid')) {
        // On native devices, camera should be available
        return true;
      } else {
        // On web, check for getUserMedia support
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
      }
    } catch (error) {
      console.error('Error checking camera availability:', error);
      return false;
    }
  }

  /**
   * Request camera permissions
   * @returns Promise<boolean> - true if permission granted
   */
  async requestCameraPermissions(): Promise<boolean> {
    try {
      if (this.platform.is('hybrid')) {
        // Permissions are handled by Capacitor Camera plugin
        return true;
      } else {
        // On web, request permission via getUserMedia
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        stream.getTracks().forEach(track => track.stop());
        return true;
      }
    } catch (error) {
      console.error('Camera permission denied:', error);
      return false;
    }
  }

  /**
   * Convert base64 to blob for file upload
   * @param base64Data - Base64 encoded image data
   * @returns Blob
   */
  base64ToBlob(base64Data: string): Blob {
    const base64 = base64Data.split(',')[1];
    const binary = atob(base64);
    const array = [];
    for (let i = 0; i < binary.length; i++) {
      array.push(binary.charCodeAt(i));
    }
    return new Blob([new Uint8Array(array)], { type: 'image/jpeg' });
  }

  /**
   * Validate image dimensions and quality
   * @param base64Image - Base64 encoded image
   * @returns Promise<boolean>
   */
  async validateImage(base64Image: string): Promise<boolean> {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        // Check minimum dimensions for face recognition
        const minWidth = 200;
        const minHeight = 200;

        if (img.width >= minWidth && img.height >= minHeight) {
          resolve(true);
        } else {
          resolve(false);
        }
      };
      img.onerror = () => resolve(false);
      img.src = base64Image;
    });
  }
}
