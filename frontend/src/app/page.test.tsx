import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Home, { AUTH_STORAGE_KEY } from "@/app/page";

describe("Home Page Authentication Flow", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("renders the login form when unauthenticated", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /kanban studio/i, level: 1 })).not.toBeInTheDocument();
  });

  it("authenticates and transitions to the Kanban board upon successful login", async () => {
    render(<Home />);

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByRole("heading", { name: "Kanban Studio" })).toBeInTheDocument();
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBe("user");
  });

  it("displays error and remains on login form when credentials are invalid", async () => {
    render(<Home />);

    await userEvent.type(screen.getByLabelText(/username/i), "admin");
    await userEvent.type(screen.getByLabelText(/password/i), "wrongpass");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByRole("alert")).toHaveTextContent(/invalid username or password/i);
    expect(screen.queryByRole("heading", { name: "Kanban Studio" })).not.toBeInTheDocument();
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBeNull();
  });

  it("logs out and returns to the login form when clicking Log out", async () => {
    window.localStorage.setItem(AUTH_STORAGE_KEY, "user");
    render(<Home />);

    expect(screen.getByRole("heading", { name: "Kanban Studio" })).toBeInTheDocument();

    const logoutButton = screen.getByRole("button", { name: /log out/i });
    await userEvent.click(logoutButton);

    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(window.localStorage.getItem(AUTH_STORAGE_KEY)).toBeNull();
  });

  it("automatically loads the board if session exists in localStorage", () => {
    window.localStorage.setItem(AUTH_STORAGE_KEY, "user");
    render(<Home />);

    expect(screen.getByRole("heading", { name: "Kanban Studio" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /sign in/i })).not.toBeInTheDocument();
  });
});

