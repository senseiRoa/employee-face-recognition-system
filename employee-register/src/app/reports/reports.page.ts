import { Component, OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { IonicModule } from '@ionic/angular';

@Component({
  selector: 'app-reports',
  templateUrl: './reports.page.html',
  styleUrls: ['./reports.page.scss'],
  imports: [
    FormsModule,
    CommonModule,
    IonicModule,
  ],
})
export class ReportsPage implements OnInit {

  // Filter options
  filters = {
    startDate: '',
    endDate: '',
    employeeId: '',
    actionType: '',
    warehouse: ''
  };

  // Data
  accessLogs: any[] = [];
  filteredLogs: any[] = [];
  loading = false;

  // Pagination
  currentPage = 0;
  pageSize = 20;
  totalLogs = 0;

  // Summary stats
  summary = {
    totalRecords: 0,
    successfulActions: 0,
    failedActions: 0,
    uniqueEmployees: 0
  };

  constructor(
    private authService: AuthService,
    private apiService: ApiService
  ) {
    // Set default date range (last 7 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);

    this.filters.startDate = startDate.toISOString().split('T')[0];
    this.filters.endDate = endDate.toISOString().split('T')[0];
  }

  ngOnInit() {
    this.loadReports();
  }

  ionViewWillEnter() {
    this.loadReports();
  }

  /**
   * Load access logs reports
   */
  async loadReports() {
    this.loading = true;
    try {
      const token = await this.authService.getValidAccessToken();
      if (!token) return;

      const params = {
        skip: this.currentPage * this.pageSize,
        limit: this.pageSize,
        start_date: this.filters.startDate,
        end_date: this.filters.endDate
      };

      this.apiService.getAccessLogs(params, token).subscribe({
        next: (response) => {
          this.accessLogs = response || [];
          this.filteredLogs = [...this.accessLogs];
          this.calculateSummary();
          this.applyFilters();
        },
        error: (error) => {
          console.error('Error loading reports:', error);
          this.accessLogs = [];
          this.filteredLogs = [];
        },
        complete: () => {
          this.loading = false;
        }
      });
    } catch (error) {
      console.error('Error loading reports:', error);
      this.loading = false;
    }
  }

  /**
   * Apply filters to the logs
   */
  applyFilters() {
    this.filteredLogs = this.accessLogs.filter(log => {
      // Employee ID filter
      if (this.filters.employeeId && !log.employee_id?.toString().includes(this.filters.employeeId)) {
        return false;
      }

      // Action type filter
      if (this.filters.actionType && log.action_type !== this.filters.actionType) {
        return false;
      }

      // Date range is already handled by the API call

      return true;
    });

    this.calculateSummary();
  }

  /**
   * Calculate summary statistics
   */
  calculateSummary() {
    this.summary = {
      totalRecords: this.filteredLogs.length,
      successfulActions: this.filteredLogs.filter(log => log.success).length,
      failedActions: this.filteredLogs.filter(log => !log.success).length,
      uniqueEmployees: new Set(this.filteredLogs.map(log => log.employee_id)).size
    };
  }

  /**
   * Reset filters to default
   */
  resetFilters() {
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 7);

    this.filters = {
      startDate: startDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
      employeeId: '',
      actionType: '',
      warehouse: ''
    };

    this.currentPage = 0;
    this.loadReports();
  }

  /**
   * Export reports to CSV
   */
  exportToCSV() {
    if (this.filteredLogs.length === 0) {
      return;
    }

    const csvContent = this.generateCSV();
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `access_logs_${this.filters.startDate}_to_${this.filters.endDate}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  }

  /**
   * Generate CSV content
   */
  generateCSV(): string {
    const headers = ['Timestamp', 'Employee ID', 'Action Type', 'Success', 'Confidence', 'Warehouse'];
    const rows = this.filteredLogs.map(log => [
      new Date(log.timestamp).toLocaleString(),
      log.employee_id || 'N/A',
      log.action_type || 'N/A',
      log.success ? 'Success' : 'Failed',
      log.confidence ? `${(log.confidence * 100).toFixed(1)}%` : 'N/A',
      log.warehouse_name || 'N/A'
    ]);

    return [headers, ...rows].map(row =>
      row.map(field => `"${field}"`).join(',')
    ).join('\n');
  }

  /**
   * Get action type display text
   */
  getActionDisplayText(actionType: string): string {
    switch (actionType) {
      case 'clock_in': return 'Clock In';
      case 'clock_out': return 'Clock Out';
      case 'break_start': return 'Break Start';
      case 'break_end': return 'Break End';
      default: return actionType || 'Unknown';
    }
  }

  /**
   * Get action icon
   */
  getActionIcon(actionType: string): string {
    switch (actionType) {
      case 'clock_in': return 'log-in-outline';
      case 'clock_out': return 'log-out-outline';
      case 'break_start': return 'cafe-outline';
      case 'break_end': return 'checkmark-circle-outline';
      default: return 'time-outline';
    }
  }

  /**
   * Get action color
   */
  getActionColor(actionType: string): string {
    switch (actionType) {
      case 'clock_in': return 'success';
      case 'clock_out': return 'danger';
      case 'break_start': return 'warning';
      case 'break_end': return 'primary';
      default: return 'medium';
    }
  }

  /**
   * Load next page
   */
  loadNextPage() {
    this.currentPage++;
    this.loadReports();
  }

  /**
   * Load previous page
   */
  loadPreviousPage() {
    if (this.currentPage > 0) {
      this.currentPage--;
      this.loadReports();
    }
  }

  /**
   * Track by function for *ngFor optimization
   */
  trackByLogId(index: number, log: any): any {
    return log.id || index;
  }
}
