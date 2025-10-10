import { Component } from '@angular/core';
import { IonApp, IonRouterOutlet, IonMenu, IonHeader, IonToolbar, IonTitle, IonContent, IonList, IonItem, IonIcon, IonLabel, IonAccordion, IonAccordionGroup, MenuController } from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import { homeOutline, settingsOutline, phonePortraitOutline, timeOutline, barChartOutline, logOutOutline, chevronDownOutline, chevronUpOutline, personAddOutline, fingerPrintOutline, documentTextOutline, analyticsOutline } from 'ionicons/icons';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  imports: [IonApp, IonRouterOutlet, IonMenu, IonHeader, IonToolbar, IonTitle, IonContent, IonList, IonItem, IonIcon, IonLabel],
})
export class AppComponent {
  constructor(
    private router: Router,
    private authService: AuthService,
    private menuController: MenuController
  ) {
    addIcons({ 
      homeOutline, 
      settingsOutline, 
      phonePortraitOutline, 
      timeOutline, 
      barChartOutline, 
      logOutOutline,
      chevronDownOutline,
      chevronUpOutline,
      personAddOutline,
      fingerPrintOutline,
      documentTextOutline,
      analyticsOutline
    });
  }

  async navigateAndCloseMenu(path: string) {
    await this.menuController.close();
    this.router.navigate([path]);
  }

  async navigateWithViewAndCloseMenu(path: string, view: string) {
    await this.menuController.close();
    this.router.navigate([path], { 
      queryParams: { view: view } 
    });
  }

  async logout() {
    try {
      await this.authService.logout();
      this.router.navigate(['/login']);
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
}
