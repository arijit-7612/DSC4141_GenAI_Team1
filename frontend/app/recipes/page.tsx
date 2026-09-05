"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Recipe, recipesApi } from "../../lib/recipes";

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [error, setError] = useState("");

  useEffect(() => { recipesApi.list().then(setRecipes).catch((exception) => setError(exception.message)); }, []);
  return <section className="page"><div className="page-heading"><div><p className="eyebrow">Your kitchen</p><h1>Recipes</h1></div><Link className="button" href="/recipes/new">Create recipe</Link></div>
    {error && <p className="error">{error}</p>}
    {!error && recipes.length === 0 && <p className="empty-state">No recipes yet. Add one to start planning meals.</p>}
    <div className="recipe-grid">{recipes.map((recipe) => <Link href={`/recipes/${recipe.id}`} className="recipe-card" key={recipe.id}><h2>{recipe.name}</h2><p>{recipe.ingredients.length} ingredient{recipe.ingredients.length === 1 ? "" : "s"}</p></Link>)}</div>
  </section>;
}
