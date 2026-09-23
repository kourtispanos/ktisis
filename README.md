# Ktisis — Διαχείριση Εργολαβίας

Μια εφαρμογή διαχείρισης για εργολάβους/κατασκευαστές: πελάτες, έργα,
προσωπικό, οικονομικά, καιρός, ημερολόγιο και οχήματα — όλα σε ένα μέρος.

Φτιαγμένη σε **Python (FastAPI)** για το backend, **React** για το UI και
**SQLite** για βάση δεδομένων. Τρέχει **μόνο τοπικά** στον υπολογιστή σου —
τα δεδομένα σου δεν φεύγουν ποτέ σε κάποιον server.

Δύο τρόποι να τη χρησιμοποιήσεις:
- **Ανάπτυξη:** κατέβασε τον κώδικα (`git clone`) και τρέξ' τη με Python/Node.
- **Απλή χρήση:** εγκατέστησέ τη σαν κανονικό πρόγραμμα Windows, με το
  `KtisisSetup.exe` που φτιάχνεται τοπικά (δες παρακάτω) — δεν χρειάζεται
  Python ή Node.

---

# Τι κάνει

| Ενότητα | Περιγραφή |
|---|---|
| **Πελάτες** | Στοιχεία πελατών + αυτόματος υπολογισμός πληρωμένου/υπολοίπου ανά πελάτη |
| **Έργα** | Προϋπολογισμός, ημερομηνίες, **ζωντανή** παρακολούθηση εξόδων vs προϋπολογισμού, αυτόματος υπολογισμός εργάσιμων ημερών |
| **Προσωπικό & Ημερομίσθια** | Αυτόματος υπολογισμός αμοιβής (ημερομίσθιο × ημέρες) + σύνολα ανά εργάτη |
| **Έξοδα & Έσοδα** | Κατηγορίες εξόδων, ποσότητα/μονάδα μέτρου, συντελεστής ΦΠΑ ανά έσοδο |
| **Φορολογίες & Τιμολόγια** | Σύνοψη ΦΠΑ προς απόδοση, φορολογικές υποχρεώσεις, τιμολόγια με παρακολούθηση πληρωμής |
| **Καιρός** | Τρέχων καιρός + πρόγνωση 4 ημερών για όποια πόλη θες (OpenWeatherMap) |
| **Ημερολόγιο** | Οπτικό πλέγμα μήνα, κλικ σε ημέρα για υπενθυμίσεις (ραντεβού, σέρβις, προθεσμίες) |
| **Οχήματα** | Ασφάλεια, ΚΤΕΟ, τέλη κυκλοφορίας, σέρβις — με αυτόματη προειδοποίηση λήξης |
| **Αναφορές** | Μηνιαία/ετήσια αναφορά με γραφήματα: τζίρος, έξοδα, καθαρά κέρδη, περιθώριο %, κατανομή εξόδων |
| **Σύνδεση** | Εγγραφή/σύνδεση/διαγραφή λογαριασμού με κρυπτογραφημένους κωδικούς (δεν αποθηκεύεται τίποτα σε απλό κείμενο) |

---

# Εκκίνηση

Χρειάζεται [Python 3.11+](https://www.python.org/downloads/) και
[Node.js](https://nodejs.org/) εγκατεστημένα.

```bash
# 1. Κατέβασμα του κώδικα
git clone https://github.com/kourtispanos/ktisis.git
cd ktisis

# 2. Virtual environment + εξαρτήσεις backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 3. Εξαρτήσεις frontend (μόνο την πρώτη φορά, ή όποτε αλλάζουν)
cd frontend
npm install
npm run build
cd ..

# 4. Εκκίνηση
python launcher.py
```

Η εφαρμογή ανοίγει αυτόματα στον browser σου, στο `http://127.0.0.1:8000`.
Πρώτη φορά που τρέχει, πάτα «Εγγραφή» για να φτιάξεις λογαριασμό.

Για ανάπτυξη του frontend με άμεση ανανέωση αλλαγών (hot reload), αντί για
`npm run build` τρέξε `npm run dev` μέσα στο `frontend/` — θα χρειαστείς
το backend ανοιχτό ταυτόχρονα (`python launcher.py` σε άλλο terminal).

---

# Ρύθμιση καιρού (προαιρετικό)

Το tab «Καιρός» χρειάζεται δωρεάν API key από το
[openweathermap.org](https://openweathermap.org/api). Μόλις το πάρεις,
φτιάξε στη ρίζα του project ένα αρχείο `local_settings.py`:

```python
WEATHER_API_KEY = "το-δικό-σου-κλειδί-εδώ"
```

Αυτό το αρχείο δεν ανεβαίνει ποτέ στο GitHub (είναι στο `.gitignore`).

---

# Τεστ

```bash
# Backend
python -m unittest discover -s tests -v

# Frontend
cd frontend
npm test
```

Κάθε τεστ του backend τρέχει σε δική του προσωρινή βάση δεδομένων — ποτέ δεν
αγγίζει το πραγματικό `ktisis.db`.

---

# Δημιουργία exe / installer

Χρειάζεται επιπλέον [PyInstaller](https://pyinstaller.org/) και
[Inno Setup](https://jrsoftware.org/isinfo.php) εγκατεστημένα.

```bash
# 1. Χτίσε πρώτα το frontend (βλ. "Εκκίνηση" παραπάνω)

# 2. Standalone exe
pip install pyinstaller
pyinstaller --name Ktisis --onedir --noconfirm --icon assets/icon.ico launcher.py

# 3. Αντιγραφή του χτισμένου frontend δίπλα στο exe
#    (Windows: xcopy /E /I frontend\dist dist\Ktisis\frontend\dist)
cp -r frontend/dist dist/Ktisis/frontend/dist

# 4. Compile installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\installer.iss
```

Το αποτέλεσμα είναι το `installer_output\KtisisSetup.exe`. Εγκαθιστά την
εφαρμογή στο `%LOCALAPPDATA%\Programs\Ktisis` — **δεν χρειάζεται δικαιώματα
διαχειριστή**, μόνο για τον τρέχοντα χρήστη. Τα δεδομένα (`ktisis.db`) ζουν
ξεχωριστά, στο `%LOCALAPPDATA%\Ktisis`.

---

# Δομή project

```
ktisis/
├── launcher.py              Εκκίνηση: ανοίγει server + browser
├── local_settings.py         API key καιρού (δεν ανεβαίνει στο GitHub)
├── assets/                   icon.ico + πηγαίο λογότυπο, για το exe
├── installer/                installer.iss + Run Ktisis.bat (Inno Setup)
│
├── backend/
│   ├── main.py                Το FastAPI app
│   ├── database/
│   │   ├── db.py                Σύνδεση με τη βάση + βοηθητικές execute/fetch
│   │   └── create_db.py         Δημιουργία/migration πινάκων
│   ├── services/               Η λογική, ένα αρχείο ανά θεματική ενότητα
│   │   ├── people.py              Πελάτες, εργάτες, ημερομίσθια
│   │   ├── finance.py             Έξοδα, έσοδα, τιμολόγια, φορολογίες
│   │   ├── projects.py            Έργα, προϋπολογισμός, εργάσιμες μέρες
│   │   ├── vehicles.py            Οχήματα
│   │   ├── calendar_events.py     Ημερολόγιο/υπενθυμίσεις
│   │   └── reports.py             Μηνιαίες/ετήσιες αναφορές
│   ├── auth/                   Hashing κωδικών + εγγραφή/σύνδεση/διαγραφή χρήστη
│   ├── external/                weather.py — εξωτερικό API καιρού
│   └── api/                    HTTP endpoints (routes, schemas, auth guard)
│
├── frontend/                 React (Vite)
│   ├── src/pages/               Ένα αρχείο ανά tab
│   └── src/components/          Κοινά κομμάτια (φόρμες, πίνακες, γραφήματα)
│
└── tests/                    Αυτοματοποιημένα τεστ (unittest)
```

Κάθε αρχείο στο `services/` ακολουθεί το ίδιο μοτίβο: `add_x()`,
`update_x()`, `delete_x()`, `list_x()` — προβλέψιμο και εύκολο στην
πλοήγηση.

---

## ⚠️ Σημειώσεις

- Οι υπολογισμοί ΦΠΑ είναι **ενδεικτικοί** — επιβεβαίωσέ τους πάντα με
  τον λογιστή σου, δεν αποτελούν φορολογική συμβουλή.
- Η εφαρμογή τρέχει **μόνο τοπικά**· δεν είναι προσβάσιμη από το
  internet εκτός αν ρυθμίσεις εσύ port forwarding στο router σου.
- Τα δεδομένα σου ζουν σε ένα αρχείο, `ktisis.db`, δίπλα στον κώδικα.
  Κάνε τακτικά αντίγραφο ασφαλείας αυτού του αρχείου.
