"use client";

import { useEffect, useMemo, useState } from "react";
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

  return (
    <section className="page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Your week</p>
          <h1>Weekly planner</h1>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {!error && recipes.length === 0 && <p className="empty-state">No recipes available. Add a recipe to start planning your week.</p>}
      <div className="planner-grid" role="table" aria-label="Weekly meal planner">
        <div className="planner-cell planner-corner" role="columnheader" />
        {MEALS.map((meal) => <div className="planner-cell planner-header" role="columnheader" key={meal}>{meal}</div>)}
        {DAYS.map((day) => (
          <div className="planner-row" role="row" key={day}>
            <div className="planner-cell planner-day" role="rowheader">{day}</div>
            {MEALS.map((meal) => {
              const cellKey = `${day}-${meal}`;
              const selectedRecipe = plan[cellKey];
              return <div className="planner-cell planner-meal" role="cell" key={cellKey}>
                <button type="button" className={`meal-picker-trigger${selectedRecipe ? " selected" : ""}`} onClick={() => openPicker(cellKey)}>
                  {selectedRecipe ?? "Select a recipe"}
                </button>
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
      </div>
    </section>
  );
}
