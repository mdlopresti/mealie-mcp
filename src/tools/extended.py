"""
Extended Mealie tools (FORK).

- Generic API access: mealie_api_request / mealie_api_endpoints / mealie_api_schema give
  1:1 coverage of every Mealie endpoint, discovered live from the instance's /openapi.json.
- Recipe maintenance done server-side so clients get compact results:
  re-parse ingredients, partial recipe updates, kitchen tools, audits.
- Recipe images: let Mealie download an image URL, or find the image on the recipe's
  own source page (og:image / JSON-LD).
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

import httpx

try:
    from ..client import MealieClient, MealieAPIError
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from client import MealieClient, MealieAPIError


ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
_OPENAPI_CACHE: dict[str, Any] = {}
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def _api_error(e: MealieAPIError) -> str:
    return json.dumps({"error": str(e), "status_code": e.status_code, "response_body": e.response_body}, indent=2)


def _unexpected(e: Exception) -> str:
    return json.dumps({"error": f"Unexpected error: {str(e)}"}, indent=2)


def _dump(data: Any, max_chars: int) -> str:
    text = json.dumps(data, indent=2, default=str)
    if max_chars and len(text) > max_chars:
        return text[:max_chars] + f'\n... [truncated {len(text) - max_chars} chars; narrow the request or raise max_chars]'
    return text


# =============================================================================
# Generic API access
# =============================================================================

def api_request(
    method: str,
    path: str,
    params: Optional[dict] = None,
    body: Optional[Any] = None,
    max_chars: int = 20000,
) -> str:
    """Call any Mealie API endpoint with the configured token."""
    method = (method or "").upper()
    if method not in ALLOWED_METHODS:
        return json.dumps({"error": f"method must be one of {sorted(ALLOWED_METHODS)}"})
    if not path.startswith("/api/"):
        return json.dumps({"error": "path must start with /api/ (see mealie_api_endpoints)"})
    try:
        with MealieClient() as client:
            kwargs: dict[str, Any] = {}
            if params:
                kwargs["params"] = params
            if body is not None:
                kwargs["json"] = body
            result = client._make_request(method, path, **kwargs)
            return _dump({"status": "ok", "method": method, "path": path, "response": result}, max_chars)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def _load_openapi(client: MealieClient) -> dict:
    if "spec" not in _OPENAPI_CACHE:
        _OPENAPI_CACHE["spec"] = client.get("/openapi.json")
    return _OPENAPI_CACHE["spec"]


def api_endpoints(search: Optional[str] = None, tag: Optional[str] = None, limit: int = 200) -> str:
    """List Mealie endpoints from the live OpenAPI spec."""
    try:
        with MealieClient() as client:
            spec = _load_openapi(client)
        rows = []
        for path, ops in spec.get("paths", {}).items():
            for method, op in ops.items():
                if method.upper() not in ALLOWED_METHODS:
                    continue
                tags = op.get("tags", [])
                summary = op.get("summary", "")
                line = f"{method.upper()} {path} - {summary}"
                if tag and not any(tag.lower() in t.lower() for t in tags):
                    continue
                if search and search.lower() not in (line + " " + " ".join(tags)).lower():
                    continue
                rows.append({"endpoint": f"{method.upper()} {path}", "summary": summary, "tags": tags})
        return json.dumps({
            "mealie_version": spec.get("info", {}).get("version"),
            "total": len(rows),
            "endpoints": rows[:limit],
        }, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def _resolve(node: Any, spec: dict, depth: int) -> Any:
    if depth <= 0:
        return node
    if isinstance(node, dict):
        if "$ref" in node:
            name = node["$ref"].split("/")[-1]
            target = spec.get("components", {}).get("schemas", {}).get(name, {})
            return {"schema": name, **_resolve(target, spec, depth - 1)}
        return {k: _resolve(v, spec, depth) for k, v in node.items() if k not in ("example", "examples")}
    if isinstance(node, list):
        return [_resolve(v, spec, depth) for v in node]
    return node


def api_schema(method: str, path: str, depth: int = 3, max_chars: int = 20000) -> str:
    """Show parameters, request body and response schema for one endpoint."""
    try:
        with MealieClient() as client:
            spec = _load_openapi(client)
        op = spec.get("paths", {}).get(path, {}).get(method.lower())
        if not op:
            return json.dumps({"error": f"{method.upper()} {path} not found; use mealie_api_endpoints"})
        out = {
            "endpoint": f"{method.upper()} {path}",
            "summary": op.get("summary"),
            "parameters": [
                {"name": p.get("name"), "in": p.get("in"), "required": p.get("required", False),
                 "schema": _resolve(p.get("schema", {}), spec, depth)}
                for p in op.get("parameters", [])
            ],
            "requestBody": _resolve(op.get("requestBody", {}), spec, depth),
            "responses": {code: _resolve(r, spec, depth) for code, r in op.get("responses", {}).items()
                          if code.startswith("2")},
        }
        return _dump(out, max_chars)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


# =============================================================================
# Recipe helpers
# =============================================================================

def _list_all(client: MealieClient, path: str, params: Optional[dict] = None) -> list[dict]:
    items: list[dict] = []
    page = 1
    while True:
        query = {"page": page, "perPage": 200, **(params or {})}
        data = client.get(path, params=query)
        batch = data.get("items", []) if isinstance(data, dict) else (data or [])
        items.extend(batch)
        total_pages = data.get("total_pages") or data.get("totalPages") if isinstance(data, dict) else None
        if not batch or not total_pages or page >= total_pages:
            break
        page += 1
    return items


def recipes_patch(slug: str, fields: dict) -> str:
    """Update any recipe fields by name (camelCase, as in mealie_recipes_get)."""
    if not isinstance(fields, dict) or not fields:
        return json.dumps({"error": "fields must be a non-empty object"})
    protected = {"id", "slug", "groupId", "householdId", "userId", "createdAt"}
    bad = sorted(set(fields) & protected)
    if bad:
        return json.dumps({"error": f"these fields cannot be changed here: {bad}"})
    try:
        with MealieClient() as client:
            recipe = client.get(f"/api/recipes/{slug}")
            unknown = sorted(k for k in fields if k not in recipe)
            for key, value in fields.items():
                if isinstance(value, dict) and isinstance(recipe.get(key), dict):
                    recipe[key] = {**recipe[key], **value}
                else:
                    recipe[key] = value
            updated = client.put(f"/api/recipes/{slug}", json=recipe)
            return json.dumps({
                "success": True,
                "slug": updated.get("slug", slug) if isinstance(updated, dict) else slug,
                "updated_fields": sorted(fields),
                "warning": f"fields not present on the recipe before: {unknown}" if unknown else None,
            }, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


def recipes_set_tools(slug: str, tool_names: list[str], create_missing: bool = True) -> str:
    """Set a recipe's kitchen tools by name."""
    try:
        with MealieClient() as client:
            existing = {t["name"].lower(): t for t in _list_all(client, "/api/organizers/tools")}
            chosen, created, missing = [], [], []
            for name in tool_names:
                tool = existing.get(name.lower())
                if not tool and create_missing:
                    tool = client.post("/api/organizers/tools", json={"name": name})
                    existing[name.lower()] = tool
                    created.append(name)
                if tool:
                    chosen.append({"id": tool["id"], "name": tool["name"], "slug": tool.get("slug"),
                                   "groupId": tool.get("groupId")})
                else:
                    missing.append(name)
            recipe = client.get(f"/api/recipes/{slug}")
            recipe["tools"] = chosen
            client.put(f"/api/recipes/{slug}", json=recipe)
            return json.dumps({"success": True, "slug": slug, "tools": [t["name"] for t in chosen],
                               "created_tools": created, "not_found": missing}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


# -----------------------------------------------------------------------------
# Ingredient re-parse
# -----------------------------------------------------------------------------

def _source_text(ing: dict) -> str:
    """Best original text for an ingredient line."""
    if ing.get("originalText"):
        return ing["originalText"].strip()
    if ing.get("food") is None and ing.get("unit") is None:
        return (ing.get("note") or "").strip()
    return (ing.get("display") or ing.get("note") or "").strip()


def _is_unparsed(ing: dict) -> bool:
    return ing.get("food") is None and ing.get("unit") is None and bool((ing.get("note") or "").strip())


_NUM = re.compile(r"(\d+(?:\.\d+)?)")


def _servings_from_yield(recipe: dict) -> dict:
    """Derive recipeServings / recipeYieldQuantity from text like '8 servings' or '12 muffins'."""
    changes: dict = {}
    text = (recipe.get("recipeYield") or "").strip()
    if not text or (recipe.get("recipeServings") or 0) > 0 or (recipe.get("recipeYieldQuantity") or 0) > 0:
        return changes
    m = _NUM.search(text)
    if not m:
        return changes
    number = float(m.group(1))
    rest = text[m.end():].strip(" -–to0123456789.").strip()
    if re.match(r"^(servings?|people|portions?)\b", rest, re.I) or not rest:
        changes["recipeServings"] = number
        changes["recipeYield"] = ""
    else:
        changes["recipeYieldQuantity"] = number
        changes["recipeYield"] = rest
    return changes


def recipes_reparse(
    slug: str,
    parser: str = "nlp",
    min_confidence: float = 0.75,
    create_missing_foods: bool = True,
    force: bool = False,
    fix_servings: bool = True,
    dry_run: bool = False,
) -> str:
    """Parse a recipe's unstructured ingredient lines in Mealie and save structured ingredients."""
    try:
        with MealieClient() as client:
            recipe = client.get(f"/api/recipes/{slug}")
            ingredients = recipe.get("recipeIngredient") or []
            targets = [i for i, ing in enumerate(ingredients)
                       if not ing.get("title") or _source_text(ing)]
            targets = [i for i in targets if force or _is_unparsed(ingredients[i])]
            texts = [_source_text(ingredients[i]) for i in targets]
            pairs = [(i, t) for i, t in zip(targets, texts) if t]

            summary: dict[str, Any] = {"slug": slug, "lines_total": len(ingredients),
                                       "lines_parsed": 0, "low_confidence_kept_as_text": [],
                                       "created_foods": [], "unit_moved_to_note": [], "dry_run": dry_run}
            new_ingredients = list(ingredients)

            if pairs:
                parsed = client.post("/api/parser/ingredients",
                                     json={"parser": parser, "ingredients": [t for _, t in pairs]})
                food_cache: dict[str, dict] = {}
                for (idx, text), result in zip(pairs, parsed):
                    old = ingredients[idx]
                    conf = (result.get("confidence") or {}).get("average") or 0
                    ing = result.get("ingredient") or {}
                    food, unit = ing.get("food"), ing.get("unit")
                    note = (ing.get("note") or "").strip()

                    if conf < min_confidence or not food:
                        summary["low_confidence_kept_as_text"].append({"line": text, "confidence": round(conf, 2)})
                        new_ingredients[idx] = {**old, "quantity": None, "unit": None, "food": None,
                                                "note": text, "originalText": text}
                        continue

                    if food and not food.get("id"):
                        key = food["name"].strip().lower()
                        if create_missing_foods and not dry_run:
                            if key not in food_cache:
                                food_cache[key] = client.post("/api/foods", json={"name": food["name"].strip()})
                                summary["created_foods"].append(food["name"].strip())
                            food = food_cache[key]
                        elif create_missing_foods:
                            summary["created_foods"].append(food["name"].strip())
                        else:
                            summary["low_confidence_kept_as_text"].append({"line": text, "reason": "unknown food"})
                            new_ingredients[idx] = {**old, "quantity": None, "unit": None, "food": None,
                                                    "note": text, "originalText": text}
                            continue

                    if unit and not unit.get("id"):
                        summary["unit_moved_to_note"].append(unit.get("name"))
                        note = f"{unit.get('name')} {note}".strip()
                        unit = None

                    new_ingredients[idx] = {
                        **old,
                        "quantity": ing.get("quantity"),
                        "unit": unit,
                        "food": food,
                        "note": note,
                        "originalText": text,
                        "referenceId": old.get("referenceId") or ing.get("referenceId"),
                    }
                    summary["lines_parsed"] += 1

            servings = _servings_from_yield(recipe) if fix_servings else {}
            summary["servings_change"] = servings or None

            if not dry_run and (pairs or servings):
                recipe["recipeIngredient"] = new_ingredients
                recipe.update(servings)
                client.put(f"/api/recipes/{slug}", json=recipe)
            if not pairs:
                summary["note"] = "no unparsed lines (use force=True to re-parse everything)"
            return json.dumps(summary, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


# -----------------------------------------------------------------------------
# Audit
# -----------------------------------------------------------------------------

def recipes_audit(slugs: Optional[list[str]] = None) -> str:
    """One compact row per recipe with data-quality flags."""
    try:
        with MealieClient() as client:
            if not slugs:
                slugs = [r["slug"] for r in _list_all(client, "/api/recipes")]
            rows = []
            for slug in slugs:
                r = client.get(f"/api/recipes/{slug}")
                ings = r.get("recipeIngredient") or []
                flags = []
                unparsed = sum(1 for i in ings if _is_unparsed(i))
                if unparsed:
                    flags.append(f"unparsed_ingredients:{unparsed}/{len(ings)}")
                if not r.get("image"):
                    flags.append("no_image")
                if not (r.get("description") or "").strip():
                    flags.append("no_description")
                if not r.get("recipeCategory"):
                    flags.append("no_category")
                if not r.get("tags"):
                    flags.append("no_tags")
                if not r.get("tools"):
                    flags.append("no_tools")
                if not (r.get("recipeServings") or r.get("recipeYieldQuantity")):
                    flags.append("no_servings")
                if not r.get("totalTime") and not r.get("totalTimeSeconds"):
                    flags.append("no_total_time")
                if not r.get("orgURL"):
                    flags.append("no_source_url")
                rows.append({"slug": slug, "name": r.get("name"), "flags": flags})
            counts: dict[str, int] = {}
            for row in rows:
                for f in row["flags"]:
                    k = f.split(":")[0]
                    counts[k] = counts.get(k, 0) + 1
            return json.dumps({"total": len(rows), "flag_counts": counts, "recipes": rows}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


# -----------------------------------------------------------------------------
# Images
# -----------------------------------------------------------------------------

def recipes_set_image_from_url(slug: str, image_url: str) -> str:
    """Have Mealie download an image URL and set it as the recipe image."""
    try:
        with MealieClient() as client:
            result = client.post(f"/api/recipes/{slug}/image", json={"url": image_url, "includeTags": False})
            return json.dumps({"success": True, "slug": slug, "image_url": image_url, "result": result}, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)


_OG = re.compile(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)(?::src)?["\'][^>]*>', re.I)
_CONTENT = re.compile(r'content=["\']([^"\']+)["\']', re.I)
_LDJSON = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', re.I | re.S)


def _ld_image(node: Any) -> Optional[str]:
    if isinstance(node, list):
        for n in node:
            found = _ld_image(n)
            if found:
                return found
        return None
    if not isinstance(node, dict):
        return None
    types = node.get("@type")
    types = types if isinstance(types, list) else [types]
    if "Recipe" in types and node.get("image"):
        img = node["image"]
        if isinstance(img, list):
            img = img[0] if img else None
        if isinstance(img, dict):
            img = img.get("url")
        if isinstance(img, str):
            return img
    for key in ("@graph", "mainEntity"):
        if key in node:
            found = _ld_image(node[key])
            if found:
                return found
    return None


def find_image_on_page(url: str) -> Optional[str]:
    """Return the recipe image URL from a page's JSON-LD Recipe or og:image."""
    resp = httpx.get(url, headers={"User-Agent": BROWSER_UA}, timeout=20.0, follow_redirects=True)
    resp.raise_for_status()
    html = resp.text
    for block in _LDJSON.findall(html):
        try:
            found = _ld_image(json.loads(block.strip()))
            if found:
                return found
        except Exception:
            continue
    for tag in _OG.findall(html):
        m = _CONTENT.search(tag)
        if m:
            return m.group(1)
    return None


def recipes_fill_missing_images(slugs: Optional[list[str]] = None, dry_run: bool = False,
                                replace_existing: bool = False) -> str:
    """For recipes without an image, take the image from the recipe's own source page (orgURL)."""
    try:
        with MealieClient() as client:
            if not slugs:
                slugs = [r["slug"] for r in _list_all(client, "/api/recipes")]
            report: dict[str, list] = {"filled": [], "would_fill": [], "already_has_image": [],
                                       "no_source_url": [], "no_image_on_page": [], "errors": []}
            for slug in slugs:
                r = client.get(f"/api/recipes/{slug}")
                if r.get("image") and not replace_existing:
                    report["already_has_image"].append(slug)
                    continue
                source = r.get("orgURL")
                if not source:
                    report["no_source_url"].append(slug)
                    continue
                try:
                    image = find_image_on_page(source)
                except Exception as e:
                    report["errors"].append({"slug": slug, "error": f"fetch {source}: {e}"})
                    continue
                if not image:
                    report["no_image_on_page"].append({"slug": slug, "source": source})
                    continue
                if dry_run:
                    report["would_fill"].append({"slug": slug, "image": image})
                    continue
                try:
                    client.post(f"/api/recipes/{slug}/image", json={"url": image, "includeTags": False})
                    report["filled"].append({"slug": slug, "image": image})
                except MealieAPIError as e:
                    report["errors"].append({"slug": slug, "error": str(e)})
            report["already_has_image"] = len(report["already_has_image"])  # type: ignore
            return json.dumps(report, indent=2)
    except MealieAPIError as e:
        return _api_error(e)
    except Exception as e:
        return _unexpected(e)
