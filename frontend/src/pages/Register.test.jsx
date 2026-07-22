import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import Register from "./Register";
import { AuthProvider } from "../context/AuthContext";
import { server } from "../mocks/server";

const mockNavigate = vi.fn();

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

function renderRegister() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Register />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Register", () => {
  beforeEach(() => {
    localStorage.clear();
    mockNavigate.mockClear();
  });

  it("renders username, email, and password fields", () => {
    renderRegister();
    expect(screen.getByLabelText("Username")).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("registers, auto-logs in, and navigates to /", async () => {
    renderRegister();

    await userEvent.type(screen.getByLabelText("Username"), "testuser");
    await userEvent.type(screen.getByLabelText("Email"), "test@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/"));
    // Register internally calls login, so a real token should be stored
    expect(localStorage.getItem("token")).toBe("fake-jwt-token");
  });

  it("shows the server's error detail on failed registration (e.g. duplicate username)", async () => {
    server.use(
      http.post("http://127.0.0.1:8000/api/auth/register", () =>
        HttpResponse.json({ detail: "Username already registered" }, { status: 400 })
      )
    );

    renderRegister();

    await userEvent.type(screen.getByLabelText("Username"), "testuser");
    await userEvent.type(screen.getByLabelText("Email"), "test@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() =>
      expect(screen.getByText("Username already registered")).toBeInTheDocument()
    );
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("enforces an 8-character minimum on the password field", () => {
    renderRegister();
    expect(screen.getByLabelText("Password")).toHaveAttribute("minLength", "8");
  });
});