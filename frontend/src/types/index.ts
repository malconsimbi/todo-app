export interface Todo {
  id: string;
  title: string;
  completed: boolean;
  owner: string;
}

export interface AuthState {
  token: string | null;
  username: string | null;
}

export interface ApiError {
  detail: string;
}