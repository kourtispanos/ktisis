import { useEffect, useState } from "react";
import { api } from "../api.js";
import { Form } from "../components/forms.jsx";
import { Card, Notice } from "../components/ui.jsx";

const capitalize = (text) => text.charAt(0).toUpperCase() + text.slice(1);

function Result({ city, data }) {
  const { current, forecast } = data;
  return (
    <>
      <div className="weather-now">
        <div className="icon">{current.emoji}</div>
        <div>
          <h3>{city}</h3>
          <div className="temp">{current.temperature.toFixed(1)}°C</div>
          <div>{capitalize(current.description)}</div>
          <div className="caption">
            Αίσθηση σαν {current.feels_like.toFixed(1)}°C · Υγρασία {current.humidity}% · Άνεμος {current.wind_speed} m/s
          </div>
        </div>
      </div>
      {forecast.length > 0 && (
        <div>
          <h3 style={{ marginTop: 16 }}>Επόμενες μέρες</h3>
          <div className="forecast">
            {forecast.map((day) => (
              <div key={day.date} className="day">
                <strong>
                  {new Date(`${day.date}T00:00`).toLocaleDateString("el-GR", { weekday: "short", day: "2-digit", month: "2-digit" })}
                </strong>
                <div className="icon">{day.emoji}</div>
                <div className="caption">{day.temp_min.toFixed(0)}° / {day.temp_max.toFixed(0)}°</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}

export default function WeatherTab() {
  const [city, setCity] = useState("Athens");
  const [state, setState] = useState({ status: "loading" });

  useEffect(() => {
    let cancelled = false;
    // Η κλήση στο εξωτερικό API μπορεί να αργήσει - η σελίδα εμφανίζεται αμέσως
    api.get(`/weather?city=${encodeURIComponent(city)}`).then(
      (data) => !cancelled && setState({ status: "ok", data }),
      () => !cancelled && setState({ status: "error" }),
    );
    return () => { cancelled = true; };
  }, [city]);

  return (
    <>
      <Card>
        <Form
          fields={[{ name: "city", label: "Πόλη", required: true }]}
          initial={{ city }}
          submitLabel="Αναζήτηση"
          onSubmit={(values) => { setState({ status: "loading" }); setCity(values.city); }}
        />
      </Card>
      <Card>
        {state.status === "loading" && <Notice>Φόρτωση καιρού...</Notice>}
        {state.status === "error" && (
          <Notice>
            Δεν βρέθηκε ο καιρός. Έλεγξε ότι έχεις βάλει σωστό API key στο local_settings.py
            και ότι η πόλη γράφεται σωστά (π.χ. &apos;Athens&apos;).
          </Notice>
        )}
        {state.status === "ok" && <Result city={city} data={state.data} />}
      </Card>
    </>
  );
}
