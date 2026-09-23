import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import { Form, ToastProvider } from "./forms.jsx";

function renderForm(props) {
  return render(
    <ToastProvider>
      <Form {...props} />
    </ToastProvider>,
  );
}

describe("Form", () => {
  test("δείχνει τις ετικέτες όλων των πεδίων", () => {
    renderForm({
      fields: [{ name: "name", label: "Όνομα" }, { name: "phone", label: "Τηλέφωνο" }],
      submitLabel: "Προσθήκη",
      onSubmit: vi.fn(),
    });
    expect(screen.getByText("Όνομα")).toBeInTheDocument();
    expect(screen.getByText("Τηλέφωνο")).toBeInTheDocument();
  });

  test("υποχρεωτικό πεδίο που λείπει εμποδίζει το submit", async () => {
    const onSubmit = vi.fn();
    renderForm({
      fields: [{ name: "name", label: "Όνομα", required: true }],
      submitLabel: "Προσθήκη",
      onSubmit,
    });
    fireEvent.click(screen.getByText("Προσθήκη"));
    await waitFor(() => expect(screen.getByText(/είναι υποχρεωτικό/)).toBeInTheDocument());
    expect(onSubmit).not.toHaveBeenCalled();
  });

  test("στέλνει τις τιμές που συμπλήρωσε ο χρήστης, με σωστούς τύπους", async () => {
    const onSubmit = vi.fn().mockResolvedValue();
    renderForm({
      fields: [
        { name: "name", label: "Όνομα", required: true },
        { name: "amount", label: "Ποσό", type: "number" },
        { name: "notes", label: "Σημειώσεις" },
      ],
      submitLabel: "Προσθήκη",
      onSubmit,
    });

    fireEvent.change(screen.getByLabelText("Όνομα"), { target: { value: "Γιάννης" } });
    fireEvent.change(screen.getByLabelText("Ποσό"), { target: { value: "150.5" } });
    fireEvent.click(screen.getByText("Προσθήκη"));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce());
    expect(onSubmit).toHaveBeenCalledWith({ name: "Γιάννης", amount: 150.5, notes: null });
  });

  test("checkbox στέλνεται ως boolean", async () => {
    const onSubmit = vi.fn().mockResolvedValue();
    renderForm({
      fields: [{ name: "paid", label: "Πληρωμένο", type: "checkbox" }],
      submitLabel: "Προσθήκη",
      onSubmit,
    });
    fireEvent.click(screen.getByLabelText("Πληρωμένο"));
    fireEvent.click(screen.getByText("Προσθήκη"));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith({ paid: true }));
  });

  test("select ξεκινάει με την πρώτη επιλογή και στέλνει την τιμή που διάλεξε ο χρήστης", async () => {
    const onSubmit = vi.fn().mockResolvedValue();
    renderForm({
      fields: [{
        name: "status", label: "Κατάσταση", type: "select",
        options: [{ value: "ενεργό", label: "ενεργό" }, { value: "ολοκληρωμένο", label: "ολοκληρωμένο" }],
      }],
      submitLabel: "Προσθήκη",
      onSubmit,
    });
    fireEvent.change(screen.getByLabelText("Κατάσταση"), { target: { value: "1" } });
    fireEvent.click(screen.getByText("Προσθήκη"));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith({ status: "ολοκληρωμένο" }));
  });

  test("προσυμπληρώνει τιμές από το initial (π.χ. επεξεργασία εγγραφής)", () => {
    renderForm({
      fields: [{ name: "name", label: "Όνομα" }],
      initial: { name: "Μαρία" },
      submitLabel: "Ενημέρωση",
      onSubmit: vi.fn(),
    });
    expect(screen.getByLabelText("Όνομα")).toHaveValue("Μαρία");
  });

  test("σφάλμα από το onSubmit εμφανίζεται σαν μήνυμα, δεν σκάει η εφαρμογή", async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error("Το όνομα χρήστη υπάρχει ήδη"));
    renderForm({
      fields: [{ name: "name", label: "Όνομα" }],
      submitLabel: "Προσθήκη",
      onSubmit,
    });
    fireEvent.click(screen.getByText("Προσθήκη"));
    await waitFor(() => expect(screen.getByText("Το όνομα χρήστη υπάρχει ήδη")).toBeInTheDocument());
  });
});
