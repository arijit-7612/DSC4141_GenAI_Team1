"use client";

import { useEffect, useState } from "react";
import { UserProfile, userProfileApi } from "../../lib/recipes";

const DIETARY_OPTIONS = [
  { id: "Vegetarian", label: "Vegetarian", desc: "No meat, poultry, or fish" },
  { id: "Vegan", label: "Vegan", desc: "No animal products or byproducts" },
  { id: "Dairy-Free", label: "Dairy-Free", desc: "No lactose, milk, or dairy products" },
  { id: "Gluten-Free", label: "Gluten-Free", desc: "No wheat, barley, rye, or gluten" },
  { id: "High-Protein", label: "High-Protein", desc: "Focus on protein-rich meals (≥25g / serv)" },
  { id: "Low-Carb", label: "Low-Carb", desc: "Reduced carbohydrates (≤20g / serv)" },
];

const ALLERGEN_OPTIONS = [
  { id: "Milk", label: "Milk / Dairy" },
  { id: "Eggs", label: "Eggs" },
  { id: "Wheat / Gluten", label: "Wheat / Gluten" },
  { id: "Soy", label: "Soy" },
  { id: "Peanuts", label: "Peanuts" },
  { id: "Tree Nuts", label: "Tree Nuts (Almonds, Walnuts, etc.)" },
  { id: "Fish", label: "Fish" },
  { id: "Shellfish", label: "Shellfish" },
];

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [preferences, setPreferences] = useState<string[]>([]);
  const [allergies, setAllergies] = useState<string[]>([]);
  const [customAllergy, setCustomAllergy] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    userProfileApi
      .get()
      .then((data) => {
        setProfile(data);
        setPreferences(data.dietary_preferences);
        setAllergies(data.allergies);
      })
      .catch((err) => setErrorMsg(err.message))
      .finally(() => setLoading(false));
  }, []);

  const togglePreference = (item: string) => {
    setPreferences((prev) =>
      prev.includes(item) ? prev.filter((p) => p !== item) : [...prev, item]
    );
  };

  const toggleAllergy = (item: string) => {
    setAllergies((prev) =>
      prev.includes(item) ? prev.filter((a) => a !== item) : [...prev, item]
    );
  };

  const addCustomAllergy = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = customAllergy.trim();
    if (trimmed && !allergies.includes(trimmed)) {
      setAllergies((prev) => [...prev, trimmed]);
      setCustomAllergy("");
    }
  };

  const removeAllergy = (item: string) => {
    setAllergies((prev) => prev.filter((a) => a !== item));
  };

  const handleSave = async () => {
    setSaving(true);
    setSuccessMsg("");
    setErrorMsg("");
    try {
      const updated = await userProfileApi.update({
        dietary_preferences: preferences,
        allergies: allergies,
      });
      setProfile(updated);
      setSuccessMsg("Dietary profile and allergy settings saved successfully!");
      setTimeout(() => setSuccessMsg(""), 4000);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <section className="page narrow">
        <div className="content-card loading-card">
          <span className="spinner" aria-hidden="true" />
          Loading your dietary profile…
        </div>
      </section>
    );
  }

  return (
    <section className="page narrow">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Your preferences</p>
          <h1>Dietary profile & allergies</h1>
          <p className="page-description">
            Customize your dietary goals and allergy warnings. Recipes matching your allergies will
            display immediate safety warnings.
          </p>
        </div>
        <button className="button" onClick={handleSave} disabled={saving}>
          {saving ? "Saving…" : "Save preferences"}
        </button>
      </div>

      {successMsg && (
        <div className="success-banner" role="status">
          ✓ {successMsg}
        </div>
      )}

      {errorMsg && (
        <div className="error-panel" role="alert">
          {errorMsg}
        </div>
      )}

      <div className="profile-sections-grid">
        {/* Dietary Preferences Card */}
        <section className="content-card profile-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Lifestyle</p>
              <h2>Dietary Preferences</h2>
              <p className="sub-description">
                Select diets you follow to highlight matching recipes.
              </p>
            </div>
          </div>

          <div className="checkbox-options-grid">
            {DIETARY_OPTIONS.map((opt) => {
              const isChecked = preferences.includes(opt.id);
              return (
                <label
                  key={opt.id}
                  className={`profile-option-pill ${isChecked ? "selected" : ""}`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => togglePreference(opt.id)}
                  />
                  <div className="option-text">
                    <strong>{opt.label}</strong>
                    <span>{opt.desc}</span>
                  </div>
                </label>
              );
            })}
          </div>
        </section>

        {/* Allergen Restrictions Card */}
        <section className="content-card profile-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Safety</p>
              <h2>Allergens & Sensitivities</h2>
              <p className="sub-description">
                Recipes containing these ingredients will trigger an allergen alert.
              </p>
            </div>
          </div>

          <div className="checkbox-options-grid">
            {ALLERGEN_OPTIONS.map((opt) => {
              const isChecked = allergies.includes(opt.id);
              return (
                <label
                  key={opt.id}
                  className={`profile-option-pill allergy-pill ${isChecked ? "selected-allergy" : ""}`}
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => toggleAllergy(opt.id)}
                  />
                  <div className="option-text">
                    <strong>{opt.label}</strong>
                  </div>
                </label>
              );
            })}
          </div>

          {/* Custom Allergy Adder */}
          <div className="custom-allergy-block">
            <label className="sub-heading" htmlFor="custom-allergy-input">
              Other Specific Allergy or Ingredient to Avoid:
            </label>
            <form onSubmit={addCustomAllergy} className="custom-allergy-form">
              <input
                id="custom-allergy-input"
                type="text"
                value={customAllergy}
                onChange={(e) => setCustomAllergy(e.target.value)}
                placeholder="e.g. Sesame, Mustard, Celery..."
              />
              <button type="submit" className="button secondary sm-button" disabled={!customAllergy.trim()}>
                + Add
              </button>
            </form>

            {allergies.filter((a) => !ALLERGEN_OPTIONS.some((o) => o.id === a)).length > 0 && (
              <div className="custom-tags-list">
                {allergies
                  .filter((a) => !ALLERGEN_OPTIONS.some((o) => o.id === a))
                  .map((custom) => (
                    <span key={custom} className="allergen-chip removable">
                      ⚠️ {custom}
                      <button
                        type="button"
                        onClick={() => removeAllergy(custom)}
                        aria-label={`Remove ${custom}`}
                      >
                        ×
                      </button>
                    </span>
                  ))}
              </div>
            )}
          </div>
        </section>
      </div>

      <div className="profile-bottom-actions">
        <button className="button" onClick={handleSave} disabled={saving}>
          {saving ? "Saving changes…" : "Save all preferences"}
        </button>
      </div>
    </section>
  );
}
