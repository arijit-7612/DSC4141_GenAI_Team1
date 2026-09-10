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
  const [deleting, setDeleting] = useState(false);

  useEffect(() => { recipesApi.get(id).then(setRecipe).catch((exception) => setError(exception.message)); }, [id]);
  if (error) return <section className="page narrow"><div className="error-panel" role="alert"><strong>We couldn’t load this recipe.</strong><span>{error}</span><Link className="button secondary" href="/recipes">Back to recipes</Link></div></section>;
  if (!recipe) return <section className="page narrow"><div className="content-card loading-card"><span className="spinner" aria-hidden="true" />Loading recipe…</div></section>;
  const currentRecipe = recipe;
  async function remove() { if (window.confirm(`Delete ${currentRecipe.name}? This can’t be undone.`)) { setDeleting(true); try { await recipesApi.remove(currentRecipe.id); router.push("/recipes"); } catch (exception) { setError(exception instanceof Error ? exception.message : "Unable to delete recipe."); setDeleting(false); } } }

  return <section className="page narrow"><Link className="back-link" href="/recipes">← Back to recipes</Link><div className="page-heading"><div><p className="eyebrow">Recipe details</p><h1>{currentRecipe.name}</h1><p className="page-description">{currentRecipe.ingredients.length} ingredient{currentRecipe.ingredients.length === 1 ? "" : "s"} in this recipe.</p></div><button className="button danger" disabled={deleting} onClick={remove}>{deleting ? "Deleting…" : "Delete"}</button></div>
    {editing ? <RecipeForm initialValue={currentRecipe} submitLabel="Save changes" onSubmit={async (payload) => { const updated = await recipesApi.update(currentRecipe.id, payload); setRecipe(updated); setEditing(false); }} /> : <><section className="ingredients-list content-card"><div className="section-heading"><div><p className="eyebrow">What you need</p><h2>Ingredients</h2></div><span className="count-badge">{currentRecipe.ingredients.length}</span></div><ul>{currentRecipe.ingredients.map((ingredient) => <li key={ingredient.id}><span className="ingredient-name">{ingredient.name}</span><span>{ingredient.quantity} {ingredient.unit}</span></li>)}</ul></section><button className="button" onClick={() => setEditing(true)}>Edit recipe</button></>}
  </section>;
}
