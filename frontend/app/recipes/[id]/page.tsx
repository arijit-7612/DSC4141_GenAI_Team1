"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { RecipeForm } from "../../../components/RecipeForm";
import { Recipe, recipesApi } from "../../../lib/recipes";

export default function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [recipe, setRecipe] = useState<Recipe>();
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { recipesApi.get(id).then(setRecipe).catch((exception) => setError(exception.message)); }, [id]);
  if (error) return <section className="page"><p className="error">{error}</p><Link href="/recipes">Back to recipes</Link></section>;
  if (!recipe) return <section className="page"><p>Loading recipe...</p></section>;
  const currentRecipe = recipe;
  async function remove() { if (window.confirm(`Delete ${currentRecipe.name}?`)) { await recipesApi.remove(currentRecipe.id); router.push("/recipes"); } }

  return <section className="page narrow"><div className="page-heading"><div><p className="eyebrow">Recipe</p><h1>{currentRecipe.name}</h1></div><button className="button danger" onClick={remove}>Delete</button></div>
    {editing ? <RecipeForm initialValue={currentRecipe} submitLabel="Save changes" onSubmit={async (payload) => { const updated = await recipesApi.update(currentRecipe.id, payload); setRecipe(updated); setEditing(false); }} /> : <><section className="ingredients-list"><h2>Ingredients</h2><ul>{currentRecipe.ingredients.map((ingredient) => <li key={ingredient.id}>{ingredient.name}<span>{ingredient.quantity} {ingredient.unit}</span></li>)}</ul></section><button className="button" onClick={() => setEditing(true)}>Edit recipe</button></>}
  </section>;
}
