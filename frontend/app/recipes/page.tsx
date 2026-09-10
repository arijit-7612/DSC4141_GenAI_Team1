"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { EmptyState } from "../../components/EmptyState";
import { Recipe, recipesApi } from "../../lib/recipes";

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => { recipesApi.list().then(setRecipes).catch((exception) => setError(exception.message)).finally(() => setLoading(false)); }, []);
  const visibleRecipes = recipes.filter((recipe) => recipe.name.toLowerCase().includes(search.toLowerCase()));
  return <section className="page"><div className="page-heading"><div><p className="eyebrow">Your kitchen</p><h1>Recipe library</h1><p className="page-description">Your go-to recipes, all in one well-organized place.</p></div><Link href="/recipes/new" className="button">+ Add recipe</Link></div>
    <div className="toolbar"><label className="search-field"><span aria-hidden="true">⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search recipes" aria-label="Search recipes" /></label><span>{loading ? "Loading recipes…" : `${recipes.length} recipe${recipes.length === 1 ? "" : "s"}`}</span></div>
    {error && <div className="error-panel" role="alert"><strong>We couldn’t load your recipes.</strong><span>{error}</span><button className="button secondary" onClick={() => window.location.reload()}>Try again</button></div>}
    {!error && loading && <div className="recipe-grid skeleton-grid" aria-label="Loading recipes"><div /><div /><div /></div>}
    {!error && !loading && recipes.length === 0 && <EmptyState icon="☷" title="No recipes yet" description="Start building your recipe collection and make meal planning easier." actionHref="/recipes/new" actionLabel="Add a recipe" />}
    {!error && !loading && recipes.length > 0 && visibleRecipes.length === 0 && <EmptyState icon="⌕" title="No recipes found" description="Try a different search term, or add a new recipe to your collection." />}
    <div className="recipe-grid">{visibleRecipes.map((recipe) => <Link href={`/recipes/${recipe.id}`} className="recipe-card" key={recipe.id}><span className="recipe-card-icon">◒</span><h2>{recipe.name}</h2><p>{recipe.ingredients.length} ingredient{recipe.ingredients.length === 1 ? "" : "s"}</p><span className="card-link">View and edit →</span></Link>)}</div>
  </section>;
}
