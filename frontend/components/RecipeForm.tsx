"use client";

import { FormEvent, useState } from "react";
import { RecipeInput } from "../lib/recipes";

type IngredientDraft = { name: string; quantity: string; unit: string };

type Props = {
  initialValue?: RecipeInput;
  submitLabel: string;
  onSubmit: (recipe: RecipeInput) => Promise<void>;
};

const UNIT_OPTIONS = [
  "g",
  "kg",
  "ml",
  "L",
  "tsp",
  "tbsp",
  "cup",
  "piece",
  "clove",
  "slice",
  "can",
  "packet",
  "bottle",
  "bunch",
];

const blankIngredient = (): IngredientDraft => ({ name: "", quantity: "", unit: "" });

export function RecipeForm({ initialValue, submitLabel, onSubmit }: Props) {
  const [name, setName] = useState(initialValue?.name ?? "");
  const [ingredients, setIngredients] = useState<IngredientDraft[]>(
    initialValue?.ingredients.map((ingredient) => ({
      name: ingredient.name,
      quantity: String(ingredient.quantity),
      unit: ingredient.unit,
    })) ?? [blankIngredient()]
  );
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  function updateIngredient(index: number, field: keyof IngredientDraft, value: string) {
    setIngredients((current) => current.map((ingredient, itemIndex) =>
      itemIndex === index ? { ...ingredient, [field]: value } : ingredient
    ));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload: RecipeInput = {
      name: name.trim(),
      ingredients: ingredients.map((ingredient) => ({
        name: ingredient.name.trim(),
        quantity: Number(ingredient.quantity),
        unit: ingredient.unit.trim(),
      })),
    };
    if (!payload.name || payload.ingredients.some((ingredient) => !ingredient.name || !ingredient.unit || ingredient.quantity <= 0 || Number.isNaN(ingredient.quantity))) {
      setError("Enter a recipe name plus a name, positive quantity, and unit for every ingredient.");
      return;
    }
    if (new Set(payload.ingredients.map((ingredient) => ingredient.name.toLowerCase())).size !== payload.ingredients.length) {
      setError("Each ingredient may appear only once.");
      return;
    }
    setError("");
    setSaving(true);
    try {
      await onSubmit(payload);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "Unable to save recipe.");
    } finally {
      setSaving(false);
    }
  }

  return <form onSubmit={submit} className="recipe-form">
    <label>Recipe name<input value={name} onChange={(event) => setName(event.target.value)} required /></label>
    <div className="form-section">
      <div className="section-heading"><h2>Ingredients</h2><button type="button" className="button secondary" onClick={() => setIngredients((current) => [...current, blankIngredient()])}>Add ingredient</button></div>
      {ingredients.map((ingredient, index) => <div className="ingredient-row" key={index}>
        <label>Name<input value={ingredient.name} onChange={(event) => updateIngredient(index, "name", event.target.value)} required /></label>
        <label>Quantity<input type="number" min="0.01" step="any" value={ingredient.quantity} onChange={(event) => updateIngredient(index, "quantity", event.target.value)} required /></label>
        <label>Unit<select value={ingredient.unit} onChange={(event) => updateIngredient(index, "unit", event.target.value)} required><option value="">Select a unit</option>{UNIT_OPTIONS.map((unit) => <option key={unit} value={unit}>{unit}</option>)}</select></label>
        <button type="button" className="link-button" disabled={ingredients.length === 1} onClick={() => setIngredients((current) => current.filter((_, itemIndex) => itemIndex !== index))}>Remove</button>
      </div>)}
    </div>
    {error && <p className="error" role="alert">{error}</p>}
    <button className="button" disabled={saving}>{saving ? "Saving..." : submitLabel}</button>
  </form>;
}
