import { Component, Input } from '@angular/core';
import { ModalController } from '@ionic/angular';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';
import { addIcons } from 'ionicons';
import { 
  personOutline, 
  mailOutline, 
  briefcaseOutline, 
  businessOutline,
  close 
} from 'ionicons/icons';

@Component({
  selector: 'app-user-profile-modal',
  templateUrl: './user-profile-modal.component.html',
  styleUrls: ['./user-profile-modal.component.scss'],
  imports: [CommonModule, IonicModule],
  standalone: true
})
export class UserProfileModalComponent {
  @Input() user: any;

  constructor(private modalController: ModalController) {
    addIcons({
      personOutline,
      mailOutline,
      briefcaseOutline,
      businessOutline,
      close
    });
  }

  dismiss() {
    this.modalController.dismiss();
  }

  getInitials(): string {
    if (!this.user?.first_name && !this.user?.last_name) {
      return 'N/A';
    }
    const firstName = this.user?.first_name || '';
    const lastName = this.user?.last_name || '';
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  }

  getFullName(): string {
    const firstName = this.user?.first_name || '';
    const lastName = this.user?.last_name || '';
    return `${firstName} ${lastName}`.trim() || 'N/A';
  }
}