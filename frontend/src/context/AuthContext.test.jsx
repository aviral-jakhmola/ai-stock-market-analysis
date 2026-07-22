import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthProvider, useAuth } from "./AuthContext";
import { server } from "../mocks/server";
import { http, HttpResponse } from "msw";

// Small harness component to exercise the context without needing real pages
function AuthProbe() {
  const { user, loading, isAuthenticated, login, logout } = useAuth();
  if (loading) return <div>loading...</div>;
  return (
    <div>
      <div data-testid="status">{isAuthenticated ? "logged-in" : "logged-out"}</div>
      <div data-testid="username">{user?.username ?? "none"}</div>
      <button onClick={() => login("testuser", "password123")}>Log in</button>
      <button onClick={logout}>Log out</button>
    </div>
  );
}

function renderWithAuth() {
  return render(
    <AuthProvider>
      <AuthProbe />
    </AuthProvider>
  );
}

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("starts logged out with no token in storage", async () => {
    renderWithAuth();
    await waitFor(() => expect(screen.getByTestId("status")).toHaveTextContent("logged-out"));
  });

  it("logs in successfully and stores the user", async () => {
    renderWithAuth();
    await waitFor(() => expect(screen.getByTestId("status")).toHaveTextContent("logged-out"));

    await userEvent.click(screen.getByText("Log in"));

    await waitFor(() => expect(screen.getByTestId("status")).toHaveTextContent("logged-in"));
    expect(screen.getByTestId("username")).toHaveTextContent("testuser");
    expect(localStorage.getItem("token")).toBe("fake-jwt-token");
  });

  it("restores the session on mount if a valid token already exists", async () => {
    localStorage.setItem("token", "existing-token");
    renderWithAuth();

    await waitFor(() => expect(screen.getByTestId("status")).toHaveTextContent("logged-in"));
    expect(screen.getByTestId("username")).toHaveTextContent("testuser");
  });

  it("clears user state if the stored token is invalid", async () => {
    localStorage.setItem("token", "garbage-token");
    server.use(
      http.get("http://127.0.0.1:8000/api/auth/me", () =>
        HttpResponse.json({ detail: "Not authenticated" }, { status: 401 })
      )
    );

    renderWithAuth();

    await waitFor(() => expect(screen.getByTestId("status")).toHaveTextContent("logged-out"));
  });

  it("logs out and clears the token", async () => {
    renderWithAuth();
    await userEvent.click(screen.getByText("Log in"));
    await waitFor(() => expect(screen.getByTestId("status")).toHaveTextContent("logged-in"));

    await userEvent.click(screen.getByText("Log out"));

    expect(screen.getByTestId("status")).toHaveTextContent("logged-out");
    expect(localStorage.getItem("token")).toBeNull();
  });
});