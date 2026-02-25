export interface AuthUser {
  id: string;
  full_name: string;
  email: string;
}

export interface AuthSession {
  access_token: string;
  user: AuthUser;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface UpdateProfileInput {
  full_name: string;
  email: string;
}

export interface ChangePasswordInput {
  current_password: string;
  new_password: string;
}
