from fastapi.testclient import TestClient


def test_generate_plan_returns_complete_plan(client: TestClient) -> None:
    response = client.post(
        "/api/v1/plans/generate",
        json={
            "people_count": 2,
            "calorie_target_per_person": 1800,
            "daily_budget_huf": 6500,
            "goal": "weight_loss",
            "meal_types": ["breakfast", "lunch", "dinner"],
            "preferred_cuisines": ["mixed"],
            "dietary_preferences": [],
            "excluded_ingredients": [],
            "max_total_cooking_minutes_per_meal": 60,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"]
    assert len(payload["meals"]) == 3
    assert payload["shopping_list"]
    assert payload["summary"]["people_count"] == 2
    assert payload["summary"]["estimated_total_cost_huf"] > 0


def test_excluded_ingredient_is_not_used(client: TestClient) -> None:
    response = client.post(
        "/api/v1/plans/generate",
        json={
            "people_count": 1,
            "calorie_target_per_person": 1800,
            "daily_budget_huf": 5000,
            "goal": "conscious",
            "meal_types": ["dinner"],
            "preferred_cuisines": ["mixed"],
            "dietary_preferences": [],
            "excluded_ingredients": ["gomba"],
            "max_total_cooking_minutes_per_meal": 60,
        },
    )

    assert response.status_code == 201
    ingredient_names = {
        ingredient["name"]
        for meal in response.json()["meals"]
        for ingredient in meal["ingredients"]
    }
    assert all("gomba" not in name.casefold() for name in ingredient_names)


def test_saved_plan_can_be_loaded(client: TestClient) -> None:
    created = client.post(
        "/api/v1/plans/generate",
        json={
            "people_count": 1,
            "calorie_target_per_person": 2000,
            "daily_budget_huf": 5500,
            "goal": "high_protein",
        },
    )
    plan_id = created.json()["id"]

    loaded = client.get(f"/api/v1/plans/{plan_id}")
    assert loaded.status_code == 200
    assert loaded.json()["id"] == plan_id
