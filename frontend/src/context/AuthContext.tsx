import {
  useEffect,
  useState,
  type ReactNode,
} from "react";

import {
  getCurrentUser,
  login as loginRequest,
  register as registerRequest,
} from "../api/auth";

import type {
  LoginCredentials,
  RegisterData,
  User,
} from "../types/auth";

import {
  AuthContext,
  type AuthContextValue,
} from "./auth-context";

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const restoreSession = async () => {
      const token = localStorage.getItem(
        "horizon_access_token",
      );

      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();

        setUser(currentUser);
      } catch {
        localStorage.removeItem(
          "horizon_access_token",
        );

        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    void restoreSession();
  }, []);

  const login = async (
    credentials: LoginCredentials,
  ) => {
    const tokenResponse =
      await loginRequest(credentials);

    localStorage.setItem(
      "horizon_access_token",
      tokenResponse.access_token,
    );

    const currentUser = await getCurrentUser();

    setUser(currentUser);
  };

  const register = async (
    data: RegisterData,
  ) => {
    await registerRequest(data);

    await login({
      email: data.email,
      password: data.password,
    });
  };

  const logout = () => {
    localStorage.removeItem(
      "horizon_access_token",
    );

    setUser(null);
  };

  const value: AuthContextValue = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}