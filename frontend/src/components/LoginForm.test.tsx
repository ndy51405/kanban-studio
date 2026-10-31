import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { LoginForm } from "@/components/LoginForm";

describe("LoginForm", () => {
  it("renders username, password inputs and sign-in button", () => {
    render(<LoginForm onLogin={vi.fn()} />);

    expect(screen.getByRole("heading", { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("shows an error message on invalid credentials", async () => {
    const handleLogin = vi.fn();
    render(<LoginForm onLogin={handleLogin} />);

    await userEvent.type(screen.getByLabelText(/username/i), "wronguser");
    await userEvent.type(screen.getByLabelText(/password/i), "wrongpass");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(
      screen.getByRole("alert")
    ).toHaveTextContent(/invalid username or password/i);
    expect(handleLogin).not.toHaveBeenCalled();
  });

  it("calls onLogin with username when credentials are valid", async () => {
    const handleLogin = vi.fn();
    render(<LoginForm onLogin={handleLogin} />);

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(handleLogin).toHaveBeenCalledWith("user");
  });

  it("populates inputs when clicking the Demo login button", async () => {
    render(<LoginForm onLogin={vi.fn()} />);

    const demoButton = screen.getByRole("button", { name: /demo login/i });
    await userEvent.click(demoButton);

    expect(screen.getByLabelText(/username/i)).toHaveValue("user");
    expect(screen.getByLabelText(/password/i)).toHaveValue("password");
  });
});

