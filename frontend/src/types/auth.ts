export interface UserInfo {
  id: string;
  email: string;
  nom: string;
  prenom: string;
  role: string;
  permissions: string[];
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserInfo;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Role {
  id: string;
  code: string;
  label: string;
  description: string | null;
  is_system: boolean;
  permissions: Permission[];
}

export interface Permission {
  id: string;
  code: string;
  description: string;
  module: string;
}

export interface UserAccount {
  id: string;
  email: string;
  nom: string;
  prenom: string;
  telephone: string | null;
  is_active: boolean;
  role: { id: string; code: string; label: string };
  last_login_at: string | null;
  created_at: string;
}

export interface UserListResponse {
  items: UserAccount[];
  total: number;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  nom: string;
  prenom: string;
  telephone?: string;
  role_id: string;
  is_active: boolean;
}
