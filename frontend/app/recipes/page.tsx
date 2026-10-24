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

  useEffect(() => {
    recipesApi
      .list()
      .then(setRecipes)
      .catch((exception) => setError(exception.message))
      .finally(() => setLoading(false));
  }, []);

  const visibleRecipes = recipes.filter((recipe) =>
    recipe.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <section className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Your kitchen</p>
          <h1>Recipe library</h1>
          <p className="page-description">
            Your go-to recipes, with verified nutritional insights and dietary labels.
          </p>
        </div>
        <Link href="/recipes/new" className="button">
          + Add recipe
        </Link>
      </div>

      <div className="toolbar">
        <label className="search-field">
          <span aria-hidden="true">⌕</span>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search recipes"
            aria-label="Search recipes"
          />
        </label>
        <span>
          {loading
            ? "Loading recipes…"
            : `${recipes.length} recipe${recipes.length === 1 ? "" : "s"}`}
        </span>
      </div>

      {error && (
        <div className="error-panel" role="alert">
          <strong>We couldn’t load your recipes.</strong>
          <span>{error}</span>
          <button className="button secondary" onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      )}

      {!error && loading && (
        <div className="recipe-grid skeleton-grid" aria-label="Loading recipes">
          <div />
          <div />
          <div />
        </div>
      )}

      {!error && !loading && recipes.length === 0 && (
        <EmptyState
          icon="☷"
          title="No recipes yet"
          description="Start building your recipe collection and view calories, macros, and allergen warnings."
          actionHref="/recipes/new"
          actionLabel="Add a recipe"
        />
      )}

      {!error && !loading && recipes.length > 0 && visibleRecipes.length === 0 && (
        <EmptyState
          icon="⌕"
          title="No recipes found"
          description="Try a different search term, or add a new recipe to your collection."
        />
      )}

      <div className="recipe-grid">
        {visibleRecipes.map((recipe) => {
          const nutrition = recipe.nutrition;
          return (
            <div className="recipe-card" key={recipe.id}>
              <div className="recipe-card-top">
                <span className="recipe-card-icon" aria-hidden="true">
                  ◒
                </span>
                <Link
                  href={`/recipes/${recipe.id}?edit=true`}
                  className="recipe-card-edit-btn"
                  title="Edit recipe"
                  aria-label={`Edit ${recipe.name}`}
                >
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                  </svg>
                  <span>Edit</span>
                </Link>
              </div>

              <Link href={`/recipes/${recipe.id}`} className="recipe-card-body">
                <h2 className="recipe-card-title">{recipe.name}</h2>

                <div className="recipe-nutrition-preview">
                  {nutrition ? (
                    <>
                      <div className="nutrition-calories-row">
                        <span className="calories-num">{nutrition.per_serving.calories}</span>
                        <span className="calories-label">kcal</span>
                        <span className="nutrition-dot" aria-hidden="true">·</span>
                        <span className="servings-subtext">per serving</span>
                      </div>
                      <div className="macros-compact-row">
                        <span className="macro-chip" title="Protein">
                          <span className="macro-chip-label">P</span>
                          <strong>{Math.round(nutrition.per_serving.protein)}g</strong>
                        </span>
                        <span className="macro-chip" title="Carbohydrates">
                          <span className="macro-chip-label">C</span>
                          <strong>{Math.round(nutrition.per_serving.carbohydrates)}g</strong>
                        </span>
                        <span className="macro-chip" title="Fat">
                          <span className="macro-chip-label">F</span>
                          <strong>{Math.round(nutrition.per_serving.fat)}g</strong>
                        </span>
                      </div>
                      {nutrition.dietary_tags.length > 0 && (
                        <div className="dietary-tags-preview">
                          {nutrition.dietary_tags.slice(0, 2).map((tag) => (
                            <span key={tag} className="dietary-pill">
                              {tag}
                            </span>
                          ))}
                          {nutrition.dietary_tags.length > 2 && (
                            <span className="dietary-pill more">
                              +{nutrition.dietary_tags.length - 2}
                            </span>
                          )}
                        </div>
                      )}
                    </>
                  ) : (
                    <p className="no-nutrition-text">Nutrition data calculating…</p>
                  )}
                </div>
              </Link>
            </div>
          );
        })}
      </div>
    </section>
  );
}
