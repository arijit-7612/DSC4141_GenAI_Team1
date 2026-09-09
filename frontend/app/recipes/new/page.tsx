"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { RecipeForm } from "../../../components/RecipeForm";
import { recipesApi } from "../../../lib/recipes";

export default function NewRecipePage() {
  const router = useRouter();
  const [created, setCreated] = useState(false);

  return <>
    <section className="page narrow"><p className="eyebrow">New recipe</p><h1>Create a recipe</h1><RecipeForm submitLabel="Create recipe" onSubmit={async (recipe) => { await recipesApi.create(recipe); setCreated(true); }} /></section>
    {created && <div className="dialog-backdrop" role="presentation">
      <div className="success-dialog" role="dialog" aria-modal="true" aria-labelledby="recipe-created-title">
        <div className="success-icon" aria-hidden="true">✓</div>
        <p className="eyebrow">Success</p>
        <h2 id="recipe-created-title">Recipe created</h2>
        <p>Your recipe has been saved to your recipe library.</p>
        <button className="button" onClick={() => router.push("/")}>Go to home</button>
      </div>
    </div>}
  </>;
}
