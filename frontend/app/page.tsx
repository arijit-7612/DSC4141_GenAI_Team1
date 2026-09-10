"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { EmptyState } from "../components/EmptyState";
import { Recipe, recipesApi } from "../lib/recipes";

export default function Home() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { recipesApi.list().then(setRecipes).catch(() => setError("We couldn’t load your recipes right now.")).finally(() => setLoading(false)); }, []);

  return (
    <section className="dashboard">
      <div className="hero">
        <div>
          <p className="eyebrow">Your healthier routine starts here</p>
          <h1>Plan your meals.<br />Eat better. Shop smarter.</h1>
          <p className="hero-copy">Build a recipe collection, map out your week, and make every trip to the kitchen a little simpler.</p>
          <div className="hero-actions"><Link href="/weekly-planner" className="button">Plan your week</Link><Link href="/recipes" className="button secondary">Browse recipes</Link></div>
        </div>
        <div className="hero-art" aria-hidden="true"><span>🥬</span><span>🥕</span><span>🍋</span><div className="hero-art-card">A calmer way<br />to eat well</div></div>
      </div>
      <div className="overview-grid">
        <article className="overview-card"><span className="overview-icon">⌘</span><p>Your recipes</p><strong>{loading ? "—" : recipes.length}</strong><span>Recipes in your library</span></article>
        <Link href="/weekly-planner" className="overview-card overview-link"><span className="overview-icon">▦</span><p>Weekly planner</p><strong>Plan meals</strong><span>Shape your week around your recipes →</span></Link>
        <Link href="/grocery-list" className="overview-card overview-link"><span className="overview-icon">✓</span><p>Grocery list</p><strong>Stay prepared</strong><span>Keep your next shop organized →</span></Link>
      </div>

      <section className="dashboard-section"><div className="section-heading"><div><p className="eyebrow">Recipe library</p><h2>Recently added</h2></div><Link href="/recipes" className="text-link">View all recipes →</Link></div>
        {loading ? <div className="recipe-grid skeleton-grid" aria-label="Loading recipes"><div /><div /><div /></div> : error ? <div className="error-panel" role="alert"><strong>{error}</strong><button className="button secondary" onClick={() => window.location.reload()}>Try again</button></div> : recipes.length === 0 ? <EmptyState icon="☷" title="No recipes yet" description="Start building your recipe collection for easier weeks ahead." actionHref="/recipes/new" actionLabel="Add a recipe" /> : <div className="recipe-grid">{recipes.slice(0, 3).map((recipe) => <Link href={`/recipes/${recipe.id}`} className="recipe-card" key={recipe.id}><span className="recipe-card-icon">◒</span><h3>{recipe.name}</h3><p>{recipe.ingredients.length} ingredient{recipe.ingredients.length === 1 ? "" : "s"}</p><span className="card-link">View recipe →</span></Link>)}</div>}
      </section>
    </section>
  );
}
