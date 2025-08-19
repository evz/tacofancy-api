import json

import pytest

from app.models import BaseLayer, Condiment, Mixin, Seasoning, Shell, db


@pytest.fixture
def sample_base_layer():
    """Create a sample base layer for testing."""
    base_layer = BaseLayer(
        url="https://example.com/carnitas",
        name="Carnitas",
        slug="carnitas",
        recipe="Slow-cooked pork shoulder with spices",
    )
    db.session.add(base_layer)
    db.session.flush()  # Get ID without committing
    return base_layer


@pytest.fixture
def sample_condiment():
    """Create a sample condiment for testing."""
    condiment = Condiment(
        url="https://example.com/salsa_verde",
        name="Salsa Verde",
        slug="salsa_verde",
        recipe="Tomatillos, jalapeños, cilantro",
    )
    db.session.add(condiment)
    db.session.flush()
    return condiment


@pytest.fixture
def taco_ingredients():
    """Create a full set of taco ingredients for testing."""
    base_layer = BaseLayer(
        url="https://example.com/carnitas",
        name="Carnitas",
        slug="carnitas",
        recipe="Slow-cooked pork shoulder",
    )
    condiment = Condiment(
        url="https://example.com/salsa_verde",
        name="Salsa Verde",
        slug="salsa_verde",
        recipe="Tomatillo salsa",
    )
    mixin = Mixin(
        url="https://example.com/onions",
        name="Diced Onions",
        slug="diced_onions",
        recipe="Fresh white onions",
    )
    seasoning = Seasoning(
        url="https://example.com/cumin",
        name="Cumin",
        slug="cumin",
        recipe="Ground cumin spice",
    )
    shell = Shell(
        url="https://example.com/corn_tortillas",
        name="Corn Tortillas",
        slug="corn_tortillas",
        recipe="Fresh corn tortillas",
    )

    db.session.add_all([base_layer, condiment, mixin, seasoning, shell])
    db.session.flush()

    return {
        "base_layer": base_layer,
        "condiment": condiment,
        "mixin": mixin,
        "seasoning": seasoning,
        "shell": shell,
    }


class TestAPI:
    """Test API endpoints."""

    def test_base_layer_by_slug(self, client, sample_base_layer):
        """Test getting specific base layer by slug."""
        response = client.get("/base_layers/carnitas/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Carnitas"
        assert data["slug"] == "carnitas"

    def test_base_layer_not_found(self, client):
        """Test getting non-existent base layer."""
        response = client.get("/base_layers/nonexistent/")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "not found" in data["message"]

    def test_base_layers_list(self, client, sample_base_layer):
        """Test getting list of base layers."""
        response = client.get("/base_layers/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["name"] == "Carnitas"

    def test_condiments_endpoint(self, client, sample_condiment):
        """Test condiments endpoints work."""
        # Test list
        response = client.get("/condiments/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["name"] == "Salsa Verde"

        # Test individual item
        response = client.get("/condiments/salsa_verde/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["name"] == "Salsa Verde"

    def test_all_ingredient_endpoints(self, client, taco_ingredients):
        """Test all ingredient type endpoints return data."""
        endpoints = ["mixins", "seasonings", "shells"]
        for endpoint in endpoints:
            response = client.get(f"/{endpoint}/")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert "name" in data[0]

    def test_random_endpoint(self, client, taco_ingredients):
        """Test random endpoint with available ingredients."""
        response = client.get("/random/")
        assert response.status_code == 200
        data = json.loads(response.data)

        # Should have all ingredient types
        expected_keys = ["base_layer", "condiment", "mixin", "seasoning", "shell"]
        for key in expected_keys:
            assert key in data
            assert data[key]["name"] is not None

    def test_contributor_not_found(self, client):
        """Test getting non-existent contributor returns 404."""
        response = client.get("/contributions/nonexistent/")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_invalid_recipe_type(self, client):
        """Test invalid recipe types return 404."""
        response = client.get("/contributors/invalid_type/")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_index_route(self, client, taco_ingredients):
        """Test the index page renders successfully."""
        response = client.get("/")
        assert response.status_code == 200

    def test_permalink_route(self, client, taco_ingredients):
        """Test permalink route with valid ingredients."""
        response = client.get("/carnitas/diced_onions/salsa_verde/cumin/corn_tortillas/")
        assert response.status_code == 200

    def test_permalink_invalid_path(self, client):
        """Test permalink route with invalid path redirects to index."""
        response = client.get("/invalid/path/")
        assert response.status_code == 302
