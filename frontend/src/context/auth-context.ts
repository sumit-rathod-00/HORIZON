import { createContext } from "react";

import type {
  LoginCredentials,
  RegisterData,
  User,
} from "../types/auth";

export interface AuthContextValue {
  user: User | null;

  isAuthenticated: boolean;

  isLoading: boolean;

  login: (
    credentials: LoginCredentials,
  ) => Promise<void>;

  register: (
    data: RegisterData,
  ) => Promise<void>;

  logout: () => void;
}

export const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  );