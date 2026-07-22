import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { http, HttpResponse } from "msw";
import Login from "./Login";
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

function renderLogin() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </MemoryRouter>
  );
}

describe("Login", () => {
  beforeEach(() => {
    localStorage.clear();
    mockNavigate.mockClear();
  });

  it("renders username and password fields", () => {
    renderLogin();
    expect(screen.getByLabelText("Username")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
  });

  it("logs in successfully and navigates to /", async () => {
    renderLogin();

    await userEvent.type(screen.getByLabelText("Username"), "testuser");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/"));
    expect(localStorage.getItem("token")).toBe("fake-jwt-token");
  });

  it("shows the server's error detail on failed login", async () => {
    server.use(
      http.post("http://127.0.0.1:8000/api/auth/login", () =>
        HttpResponse.json({ detail: "Incorrect username or password" }, { status: 401 })
      )
    );

    renderLogin();

    await userEvent.type(screen.getByLabelText("Username"), "testuser");
    await userEvent.type(screen.getByLabelText("Password"), "wrongpass");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() =>
      expect(screen.getByText("Incorrect username or password")).toBeInTheDocument()
    );
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it("falls back to a generic error if the server gives no detail", async () => {
    server.use(
      http.post("http://127.0.0.1:8000/api/auth/login", () =>
        HttpResponse.json({}, { status: 500 })
      )
    );

    renderLogin();

    await userEvent.type(screen.getByLabelText("Username"), "testuser");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: /log in/i }));

    await waitFor(() =>
      expect(screen.getByText("Login failed. Please check your credentials.")).toBeInTheDocument()
    );
  });

  it("disables the submit button while logging in", async () => {
  server.use(
    http.post("http://127.0.0.1:8000/api/auth/login", async () => {
      // Keep the request pending briefly so the loading state is visible
      await new Promise((resolve) => setTimeout(resolve, 300));

      return HttpResponse.json({
        access_token: "fake-jwt-token",
      });
    })
  );

  renderLogin();

  await userEvent.type(screen.getByLabelText("Username"), "testuser");
  await userEvent.type(screen.getByLabelText("Password"), "password123");

  const button = screen.getByRole("button", { name: /log in/i });

  // Don't await the click, so we can observe the intermediate loading state.
  userEvent.click(button);

  await waitFor(() => {
    expect(
      screen.getByRole("button", { name: /logging in/i })
    ).toBeDisabled();
  });
});
});