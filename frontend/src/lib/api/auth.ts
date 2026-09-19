import type {
  CreateUserRequest,
  LoginRequest,
  LoginResponse,
  Role,
  UserInfo,
  UserListResponse,
} from "@/types/auth";
import { apiFetch } from "./client";

export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export async function getMe(token: string): Promise<UserInfo> {
  return apiFetch<UserInfo>("/api/v1/auth/me", {}, token);
}

export async function forgotPassword(email: string): Promise<{ message: string; reset_token?: string }> {
  return apiFetch("/api/v1/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  return apiFetch("/api/v1/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

export async function checkHealth(): Promise<{
  status: string;
  environment: string;
  database: string;
  redis: string;
}> {
  return apiFetch("/api/v1/health");
}

export async function listUsers(token: string, search?: string): Promise<UserListResponse> {
  const params = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiFetch<UserListResponse>(`/api/v1/users${params}`, {}, token);
}

export async function createUser(token: string, data: CreateUserRequest) {
  return apiFetch("/api/v1/users", {
    method: "POST",
    body: JSON.stringify(data),
  }, token);
}

export async function listRoles(token: string): Promise<Role[]> {
  return apiFetch<Role[]>("/api/v1/roles", {}, token);
}
