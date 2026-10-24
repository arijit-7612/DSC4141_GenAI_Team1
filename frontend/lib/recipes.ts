export type RecipeIngredient = {
  id?: number;
  name: string;
  quantity: number;
  unit: string;
};

export type MacroNutrients = {
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  fiber: number;
  sugar: number;
  saturated_fat: number;
  sodium: number;
};

export type RecipeNutrition = {
  servings: number;
  per_serving: MacroNutrients;
  total: MacroNutrients;
  dietary_tags: string[];
  allergens: string[];
  confidence_score: number;
  unmatched_ingredients: string[];
  is_estimate: boolean;
};

export type Recipe = {
  id: number;
  name: string;
  ingredients: RecipeIngredient[];
  nutrition?: RecipeNutrition | null;
};

export type RecipeInput = Omit<Recipe, "id" | "nutrition">;

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? "Something went wrong. Please try again.");
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export const recipesApi = {
  list: () => request<Recipe[]>("/api/recipes"),
  get: (id: string | number) => request<Recipe>(`/api/recipes/${id}`),
  create: (recipe: RecipeInput) => request<Recipe>("/api/recipes", { method: "POST", body: JSON.stringify(recipe) }),
  update: (id: number, recipe: RecipeInput) => request<Recipe>(`/api/recipes/${id}`, { method: "PUT", body: JSON.stringify(recipe) }),
  remove: (id: number) => request<void>(`/api/recipes/${id}`, { method: "DELETE" }),
};

export const nutritionApi = {
  get: (recipeId: number | string, servings: number = 1) =>
    request<RecipeNutrition>(`/api/recipes/${recipeId}/nutrition?servings=${servings}`),
};

export type UserProfile = {
  id: number;
  username: string;
  dietary_preferences: string[];
  allergies: string[];
};

export const userProfileApi = {
  get: () => request<UserProfile>("/api/profile"),
  update: (profile: { dietary_preferences: string[]; allergies: string[] }) =>
    request<UserProfile>("/api/profile", {
      method: "PUT",
      body: JSON.stringify(profile),
    }),
};

export type MealPlanSlot = {
  id: number;
  day: string;
  meal: string;
  recipe_id: number;
  recipe_name: string;
};

export const mealPlanApi = {
  list: () => request<MealPlanSlot[]>("/api/meal-plan"),
  setSlot: (day: string, meal: string, recipe_id: number) =>
    request<MealPlanSlot>("/api/meal-plan", {
      method: "POST",
      body: JSON.stringify({ day, meal, recipe_id }),
    }),
  removeSlot: (day: string, meal: string) =>
    request<void>(`/api/meal-plan/${encodeURIComponent(day)}/${encodeURIComponent(meal)}`, {
      method: "DELETE",
    }),
  clear: () => request<void>("/api/meal-plan", { method: "DELETE" }),
};

export type GroceryItem = {
  name: string;
  quantity: number;
  unit: string;
  category: string;
  show_quantity: boolean;
  display_quantity: string;
  recipes: string[];
};

export type GroceryCategoryGroup = {
  category: string;
  items: GroceryItem[];
};

export type GroceryListResponse = {
  items: GroceryItem[];
  categories: GroceryCategoryGroup[];
  total_items: number;
  total_recipes: number;
  planned_meals_count: number;
};

export const groceryApi = {
  get: () => request<GroceryListResponse>("/api/grocery-list"),
};
