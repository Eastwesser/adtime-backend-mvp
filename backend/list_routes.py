# backend/list_routes.py
from fastapi import FastAPI
from app.main import app

# This func is used for frontenders to check existing routes
def list_routes(app: FastAPI):
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return routes

if __name__ == "__main__":
    routes = list_routes(app)
    print("🌐 Все доступные роуты API:")
    print("=" * 50)
    for route in sorted(routes, key=lambda x: x["path"]):
        print(f"{' | '.join(route['methods']):<20} {route['path']}")
