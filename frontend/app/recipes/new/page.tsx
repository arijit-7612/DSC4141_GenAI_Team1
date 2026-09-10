"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { RecipeForm } from "../../../components/RecipeForm";
import { recipesApi } from "../../../lib/recipes";

export default function NewRecipePage() {
  const router = useRouter();
  const [created, setCreated] = useState(false);

  return <>
    <section className="page narrow"><div className="page-intro"><p className="eyebrow">Recipe library</p><h1>Create a recipe</h1><p className="page-description">Add the ingredients you’ll need so your meals are easy to plan and shop for.</p></div><RecipeForm submitLabel="Create recipe" onSubmit={async (recipe) => { await recipesApi.create(recipe); setCreated(true); }} /></section>
    {created && <div className="dialog-backdrop" role="presentation">
      <div className="success-dialog" role="dialog" aria-modal="true" aria-labelledby="recipe-created-title">
        <div className="success-icon" aria-hidden="true">✓</div>
        <p className="eyebrow">Success</p>
        <h2 id="recipe-created-title">Recipe created</h2>
        <p>Your recipe has been saved to your recipe library.</p>
        <div className="dialog-actions"><button className="button" onClick={() => router.push("/recipes")}>View recipes</button><button className="button secondary" onClick={() => router.push("/")}>Go to home</button></div>
      </div>
    </div>}
  </>;
}
