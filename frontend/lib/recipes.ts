export type RecipeIngredient = {
  id?: number;
  name: string;
  quantity: number;
  unit: string;
};

export type Recipe = {
  id: number;
  name: string;
  ingredients: RecipeIngredient[];
};

export type RecipeInput = Omit<Recipe, "id">;

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
  get: (id: string) => request<Recipe>(`/api/recipes/${id}`),
  create: (recipe: RecipeInput) => request<Recipe>("/api/recipes", { method: "POST", body: JSON.stringify(recipe) }),
  update: (id: number, recipe: RecipeInput) => request<Recipe>(`/api/recipes/${id}`, { method: "PUT", body: JSON.stringify(recipe) }),
  remove: (id: number) => request<void>(`/api/recipes/${id}`, { method: "DELETE" }),
};
