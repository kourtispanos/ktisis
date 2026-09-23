import { describe, expect, test } from "vitest";
import { dash, money, nameMap, percent, toOptions, today, yesNo } from "./lib.js";

describe("money", () => {
  test("μορφοποιεί αριθμό με δύο δεκαδικά και σύμβολο ευρώ", () => {
    expect(money(1234.5)).toBe("1234.50 €");
  });

  test("δείχνει παύλα για null", () => {
    expect(money(null)).toBe("-");
  });

  test("δουλεύει με αρνητικά ποσά (π.χ. ζημιά)", () => {
    expect(money(-42)).toBe("-42.00 €");
  });
});

describe("percent", () => {
  test("στρογγυλοποιεί χωρίς δεκαδικά", () => {
    expect(percent(23.7)).toBe("24%");
  });

  test("δείχνει παύλα για null", () => {
    expect(percent(null)).toBe("-");
  });
});

describe("dash", () => {
  test("δείχνει παύλα για null, undefined ή κενό string", () => {
    expect(dash(null)).toBe("-");
    expect(dash(undefined)).toBe("-");
    expect(dash("")).toBe("-");
  });

  test("επιστρέφει την τιμή αν υπάρχει", () => {
    expect(dash("Αθήνα")).toBe("Αθήνα");
    expect(dash(0)).toBe(0);
  });
});

describe("yesNo", () => {
  test("μεταφράζει αληθοτιμές σε Ναι/Όχι", () => {
    expect(yesNo(1)).toBe("Ναι");
    expect(yesNo(true)).toBe("Ναι");
    expect(yesNo(0)).toBe("Όχι");
    expect(yesNo(false)).toBe("Όχι");
  });
});

describe("today", () => {
  test("επιστρέφει ημερομηνία σε μορφή YYYY-MM-DD", () => {
    expect(today()).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});

describe("toOptions / nameMap", () => {
  const rows = [
    { id: 1, name: "Γιάννης" },
    { id: 2, name: "Μαρία" },
  ];

  test("toOptions φτιάχνει { value, label } από γραμμές", () => {
    expect(toOptions(rows, (r) => r.name)).toEqual([
      { value: 1, label: "Γιάννης" },
      { value: 2, label: "Μαρία" },
    ]);
  });

  test("nameMap φτιάχνει λεξικό id -> name", () => {
    expect(nameMap(rows)).toEqual({ 1: "Γιάννης", 2: "Μαρία" });
  });
});
