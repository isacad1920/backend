import { apiClient, handleApiError,PaginatedResponse } from '../lib/api';
import type { Notification, PaginationParams } from '../types';

interface CreateNotificationRequest {
  userId?: number;
  title: string;
  body: string;
  data?: Record<string, unknown>;
}

interface SendNotificationRequest {
  userIds: number[];
  title: string;
  body: string;
  type?: 'push' | 'email' | 'both';
}

export class NotificationsService {
  async getNotifications(params: PaginationParams & { seen?: boolean } = {}): Promise<PaginatedResponse<Notification>> {
    try {
      const queryParams = new URLSearchParams();
      if (params.page) queryParams.append('page', params.page.toString());
      if (params.size) queryParams.append('size', params.size.toString());
      if (params.seen !== undefined) queryParams.append('seen', params.seen.toString());

      const query = queryParams.toString();
      return await apiClient.get<PaginatedResponse<Notification>>(`/notifications/${query ? `?${query}` : ''}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async createNotification(notificationData: CreateNotificationRequest): Promise<Notification> {
    try {
      return await apiClient.post<Notification>('/notifications/', notificationData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async markAsRead(notificationId: number): Promise<void> {
    try {
      await apiClient.put(`/notifications/${notificationId}/read`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async deleteNotification(notificationId: number): Promise<void> {
    try {
      await apiClient.delete(`/notifications/${notificationId}`);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }

  async sendNotification(notificationData: SendNotificationRequest): Promise<void> {
    try {
      await apiClient.post('/notifications/send', notificationData);
    } catch (error) {
      throw new Error(handleApiError(error));
    }
  }
}

export const notificationsService = new NotificationsService();