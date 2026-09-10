"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { EmptyState } from "../../components/EmptyState";
import { Recipe, recipesApi } from "../../lib/recipes";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const MEALS = ["Breakfast", "Lunch", "Dinner"];

type Plan = Record<string, string>;

export default function WeeklyPlannerPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [plan, setPlan] = useState<Plan>({});
  const [activeCell, setActiveCell] = useState<string>();
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    recipesApi.list()
      .then((items) => setRecipes([...items].sort((a, b) => a.name.localeCompare(b.name))))
      .catch((exception) => setError(exception instanceof Error ? exception.message : "Unable to load recipes."));
  }, []);

  const filteredRecipes = useMemo(
    () => recipes.filter((recipe) => recipe.name.toLocaleLowerCase().includes(search.toLocaleLowerCase())),
    [recipes, search],
  );

  function selectRecipe(cellKey: string, recipe: Recipe) {
    setPlan((current) => ({ ...current, [cellKey]: recipe.name }));
    setActiveCell(undefined);
    setSearch("");
  }

  function openPicker(cellKey: string) {
    setActiveCell((current) => current === cellKey ? undefined : cellKey);
    setSearch("");
  }

  function removeRecipe(cellKey: string) {
    setPlan((current) => {
      const updated = { ...current };
      delete updated[cellKey];
      return updated;
    });
  }

  return (
    <section className="page planner-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Your week</p>
          <h1>Weekly planner</h1>
          <p className="page-description">Choose a recipe for each meal and make your week feel lighter.</p>
        </div>
        <Link href="/recipes/new" className="button secondary">+ Add recipe</Link>
      </div>

      {error && <div className="error-panel" role="alert"><strong>We couldn’t load your recipes.</strong><span>{error}</span><button className="button secondary" onClick={() => window.location.reload()}>Try again</button></div>}
      {!error && recipes.length === 0 && <EmptyState icon="▦" title="Your week is waiting to be planned" description="Add a recipe first, then return here to place it into your weekly plan." actionHref="/recipes/new" actionLabel="Add a recipe" />}
      {!error && recipes.length > 0 && <div className="planner-shell"><div className="planner-grid" role="table" aria-label="Weekly meal planner">
        <div className="planner-cell planner-corner" role="columnheader" />
        {DAYS.map((day) => <div className="planner-cell planner-header" role="columnheader" key={day}>{day.slice(0, 3)}<span>{day}</span></div>)}
        {MEALS.map((meal) => (
          <div className="planner-row" role="row" key={meal}>
            <div className="planner-cell planner-day" role="rowheader">{meal}</div>
            {DAYS.map((day) => {
              const cellKey = `${day}-${meal}`;
              const selectedRecipe = plan[cellKey];
              return <div className="planner-cell planner-meal" role="cell" key={cellKey}>
                <button type="button" className={`meal-picker-trigger${selectedRecipe ? " selected" : ""}`} onClick={() => openPicker(cellKey)}>
                  {selectedRecipe ?? "Select a recipe"}
                </button>
                {selectedRecipe && <button
                    type="button"
                    className="meal-remove"
                    aria-label={`Remove recipe from ${day} ${meal}`}
                    onClick={() => removeRecipe(cellKey)}
                  >×</button>}
                {activeCell === cellKey && <div className="recipe-picker">
                  <input
                    aria-label={`Search recipes for ${day} ${meal}`}
                    autoFocus
                    placeholder="Search recipes"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                  />
                  <div className="recipe-picker-options">
                    {filteredRecipes.map((recipe) => <button type="button" key={recipe.id} onClick={() => selectRecipe(cellKey, recipe)}>{recipe.name}</button>)}
                    {filteredRecipes.length === 0 && <p>No matching recipes.</p>}
                  </div>
                </div>}
              </div>;
            })}
          </div>
        ))}
      </div></div>}
    </section>
  );
}
