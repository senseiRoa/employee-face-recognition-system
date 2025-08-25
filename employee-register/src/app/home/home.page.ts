import { Component } from '@angular/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
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
export class HomePage {
  loading = false;
  message = '';

  employee_id = '';
  name = '';

  constructor(private api: ApiService) { }

  async captureBase64(): Promise<string | null> {
    const photo = await Camera.getPhoto({
      quality: 80,
      resultType: CameraResultType.Base64,
      source: CameraSource.Camera
    });
    return photo.base64String ?? null;
  }

  async enroll() {
    this.message = '';
    if (!this.employee_id || !this.name) { this.message = 'Employee ID y Name son requeridos'; return; }
    this.loading = true;
    try {
      const b64 = await this.captureBase64();
      if (!b64) { this.message = 'No se pudo capturar la imagen'; return; }
      await this.api.registerFace(this.employee_id, this.name, b64).toPromise();
      this.message = `Registrado: ${this.employee_id}`;
    } catch (e: any) {
      this.message = e?.error?.detail || 'Error registrando rostro';
    } finally {
      this.loading = false;
    }
  }

  async check() {
    this.message = '';
    this.loading = true;
    try {
      const b64 = await this.captureBase64();
      if (!b64) { this.message = 'No se pudo capturar la imagen'; return; }
      const res: any = await this.api.checkInOut(b64).toPromise();
      if (res.recognized) {
        this.message = `${res.event?.toUpperCase()} de ${res.name} (${res.employee_id}) @ ${res.ts}`;
      } else {
        this.message = 'Rostro no reconocido';
      }
    } catch (e: any) {
      this.message = e?.error?.detail || 'Error en verificación';
    } finally {
      this.loading = false;
    }
  }
}