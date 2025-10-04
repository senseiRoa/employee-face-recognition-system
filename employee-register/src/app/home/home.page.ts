import { Component } from '@angular/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule, ToastController } from '@ionic/angular';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  imports: [
    FormsModule,
    CommonModule,
    IonicModule,
  ],
})
export class HomePage {
  loading = false;

  name = '';
  message = '';

  constructor(
    private api: ApiService,
    private toastCtrl: ToastController
  ) { }

  private async showToast(message: string, color: 'success' | 'danger' | 'warning' | 'primary' = 'primary') {
    const toast = await this.toastCtrl.create({
      message,
      duration: 3000,
      position: 'bottom',
      color,
    });
    toast.present();
  }

  async captureBase64(): Promise<string | null> {
    const photo = await Camera.getPhoto({
      quality: 80,
      resultType: CameraResultType.Base64,
      source: CameraSource.Camera
    });
    return photo.base64String ?? null;
  }

  async enroll() {
    if ( !this.name) {
      this.showToast('Name es requerido', 'warning');
      return;
    }
    this.loading = true;
    try {
      const b64 = await this.captureBase64();
      if (!b64) {
        this.showToast('No se pudo capturar la imagen', 'danger');
        return;
      }
      await this.api.registerFace( this.name, b64).toPromise();
      this.showToast(`Registrado: ${this.name}`, 'success');
    } catch (e: any) {
      this.showToast(e?.error?.detail || 'Error registrando rostro', 'danger');
    } finally {
      this.loading = false;
    }
  }

  async check() {
    this.loading = true;
    try {
      const b64 = await this.captureBase64();
      if (!b64) {
        this.showToast('No se pudo capturar la imagen', 'danger');
        return;
      }
      const res: any = await this.api.checkInOut(b64).toPromise();
      if (res.recognized) {
        this.showToast(`${res.event?.toUpperCase()} de ${res.name} (${res.employee_id}) @ ${res.ts}`, 'success');
      } else {
        this.showToast('Rostro no reconocido', 'warning');
      }
    } catch (e: any) {
      this.showToast(e?.error?.detail || 'Error en verificación', 'danger');
    } finally {
      this.loading = false;
    }
  }
}
