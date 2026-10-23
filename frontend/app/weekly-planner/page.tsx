"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { EmptyState } from "../../components/EmptyState";
import { Recipe, mealPlanApi, recipesApi } from "../../lib/recipes";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const MEALS = ["Breakfast", "Lunch", "Dinner"];

type Plan = Record<string, string>;

export default function WeeklyPlannerPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [plan, setPlan] = useState<Plan>({});
  const [activeCell, setActiveCell] = useState<string>();
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([recipesApi.list(), mealPlanApi.list()])
      .then(([recipeItems, planSlots]) => {
        setRecipes([...recipeItems].sort((a, b) => a.name.localeCompare(b.name)));
        const loadedPlan: Plan = {};
        for (const slot of planSlots) {
          loadedPlan[`${slot.day}-${slot.meal}`] = slot.recipe_name;
        }
        setPlan(loadedPlan);
      })
      .catch((exception) =>
        setError(exception instanceof Error ? exception.message : "Unable to load planner data.")
      )
      .finally(() => setLoading(false));
  }, []);

  const filteredRecipes = useMemo(
    () =>
      recipes.filter((recipe) =>
        recipe.name.toLocaleLowerCase().includes(search.toLocaleLowerCase())
      ),
    [recipes, search]
  );

  const plannedCount = Object.keys(plan).length;

  async function selectRecipe(day: string, meal: string, recipe: Recipe) {
    const cellKey = `${day}-${meal}`;
    setPlan((current) => ({ ...current, [cellKey]: recipe.name }));
    setActiveCell(undefined);
    setSearch("");
    try {
      await mealPlanApi.setSlot(day, meal, recipe.id);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "Failed to save meal plan.");
    }
  }

  function openPicker(cellKey: string) {
    setActiveCell((current) => (current === cellKey ? undefined : cellKey));
    setSearch("");
  }

  async function removeRecipe(day: string, meal: string) {
    const cellKey = `${day}-${meal}`;
    setPlan((current) => {
      const updated = { ...current };
      delete updated[cellKey];
      return updated;
    });
    try {
      await mealPlanApi.removeSlot(day, meal);
    } catch (exception) {
      setError(exception instanceof Error ? exception.message : "Failed to remove recipe.");
    }
  }

  async function clearAll() {
    if (window.confirm("Clear all planned meals for the week?")) {
      setPlan({});
      try {
        await mealPlanApi.clear();
      } catch (exception) {
        setError(exception instanceof Error ? exception.message : "Failed to clear meal plan.");
      }
    }
  }

  return (
    <section className="page planner-page">
      <div className="page-heading">
        <div>
          <p className="eyebrow">Your week</p>
          <h1>Weekly planner</h1>
          <p className="page-description">
            Choose a recipe for each meal and automatically generate your grocery list.
          </p>
        </div>
        <div className="heading-actions">
          {plannedCount > 0 && (
            <button type="button" className="button secondary danger-text" onClick={clearAll}>
              Clear plan
            </button>
          )}
          <Link href="/grocery-list" className="button">
            View grocery list {plannedCount > 0 ? `(${plannedCount})` : ""} →
          </Link>
          <Link href="/recipes/new" className="button secondary">
            + Add recipe
          </Link>
        </div>
      </div>

      {error && (
        <div className="error-panel" role="alert">
          <strong>We couldn’t update your planner.</strong>
          <span>{error}</span>
          <button className="button secondary" onClick={() => window.location.reload()}>
            Try again
          </button>
        </div>
      )}

      {!error && !loading && recipes.length === 0 && (
        <EmptyState
          icon="▦"
          title="Your week is waiting to be planned"
          description="Add a recipe first, then return here to place it into your weekly plan."
          actionHref="/recipes/new"
          actionLabel="Add a recipe"
        />
      )}

      {loading && (
        <div className="content-card loading-card">
          <span className="spinner" aria-hidden="true" />
          Loading your meal plan…
        </div>
      )}

      {!error && !loading && recipes.length > 0 && (
        <div className="planner-shell">
          <div className="planner-grid" role="table" aria-label="Weekly meal planner">
            <div className="planner-cell planner-corner" role="columnheader" />
            {DAYS.map((day) => (
              <div className="planner-cell planner-header" role="columnheader" key={day}>
                {day.slice(0, 3)}
                <span>{day}</span>
              </div>
            ))}
            {MEALS.map((meal) => (
              <div className="planner-row" role="row" key={meal}>
                <div className="planner-cell planner-day" role="rowheader">
                  {meal}
                </div>
                {DAYS.map((day) => {
                  const cellKey = `${day}-${meal}`;
                  const selectedRecipe = plan[cellKey];
                  return (
                    <div className="planner-cell planner-meal" role="cell" key={cellKey}>
                      <button
                        type="button"
                        className={`meal-picker-trigger${selectedRecipe ? " selected" : ""}`}
                        onClick={() => openPicker(cellKey)}
                      >
                        {selectedRecipe ?? "Select a recipe"}
                      </button>
                      {selectedRecipe && (
                        <button
                          type="button"
                          className="meal-remove"
                          aria-label={`Remove recipe from ${day} ${meal}`}
                          onClick={() => removeRecipe(day, meal)}
                        >
                          ×
                        </button>
                      )}
                      {activeCell === cellKey && (
                        <div className="recipe-picker">
                          <input
                            aria-label={`Search recipes for ${day} ${meal}`}
                            autoFocus
                            placeholder="Search recipes"
                            value={search}
                            onChange={(event) => setSearch(event.target.value)}
                          />
                          <div className="recipe-picker-options">
                            {filteredRecipes.map((recipe) => (
                              <button
                                type="button"
                                key={recipe.id}
                                onClick={() => selectRecipe(day, meal, recipe)}
                              >
                                {recipe.name}
                              </button>
                            ))}
                            {filteredRecipes.length === 0 && <p>No matching recipes.</p>}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
