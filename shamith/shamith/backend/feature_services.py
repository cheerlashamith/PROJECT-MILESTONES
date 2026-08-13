"""Backend implementations for CIH's recently added AI feature modules."""

from __future__ import annotations

import hashlib
import io
import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw

from backend.llama_service import LlamaService


ROOT_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT_DIR / "public"
TEMP_DIR = PUBLIC_DIR / "temp"
THEME_OUTPUT_DIR = PUBLIC_DIR / "generated_themes"
PPE_IMAGES_DIR = ROOT_DIR / "dataset_PPE" / "images" / "val"
PPE_LABELS_DIR = ROOT_DIR / "dataset_PPE" / "labels" / "val"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
THEME_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


DEFAULT_THEMES: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    "Modern White": {
        "wall": (245, 245, 245), "balcony": (60, 60, 60),
        "column": (130, 130, 130), "wood": (95, 70, 45),
    },
    "Luxury Beige": {
        "wall": (220, 205, 180), "balcony": (110, 80, 55),
        "column": (175, 165, 145), "wood": (120, 85, 55),
    },
    "Contemporary Grey": {
        "wall": (190, 190, 190), "balcony": (45, 45, 45),
        "column": (120, 120, 120), "wood": (70, 55, 40),
    },
}

PPE_CLASS_MAP = {
    0: "Helmet", 1: "Gloves", 2: "Safety Vest", 3: "Safety Boots",
    4: "Safety Goggles", 5: "NO-Safety Vest", 6: "Person",
    7: "NO-Helmet", 8: "NO-Goggles", 9: "NO-Gloves", 10: "NO-Safety Boots",
}


def extract_json_object(text: str) -> Dict[str, Any] | None:
    """Extract the first complete-looking JSON object from an LLM response."""
    if not text:
        return None
    fenced = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I | re.S)
    decoder = json.JSONDecoder()
    for index, char in enumerate(fenced):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(fenced[index:])
            return value if isinstance(value, dict) else None
        except json.JSONDecodeError:
            continue
    return None


def generate_or_raise(llama: LlamaService, prompt: str, system: str) -> str:
    response = llama.generate(prompt, system=system, temperature=0.2).strip()
    if not response:
        raise RuntimeError("Ollama returned an empty response.")
    if response.startswith("⚠️"):
        raise RuntimeError(response.replace("**", ""))
    return response


def generate_daily_report(llama: LlamaService, data: Dict[str, Any]) -> str:
    """Generate an AI-enhanced daily construction shift report."""
    report_date = str(data.get("report_date", "")).strip()
    weather = str(data.get("weather", "Not recorded")).strip()
    manpower = str(data.get("manpower", "Not recorded")).strip()
    tasks_completed = str(data.get("tasks_completed", "")).strip()
    issues = str(data.get("issues", "None reported")).strip()
    location = str(data.get("location", "")).strip()

    if not tasks_completed:
        raise ValueError("Tasks completed field is required to generate a report.")

    prompt = (
        f"You are a Construction Project Manager. Draft a professional, detailed Daily Construction Report based on the following field notes:\n\n"
        f"Date: {report_date or 'Today'}\n"
        f"Location / Site: {location or 'Not specified'}\n"
        f"Weather Conditions: {weather}\n"
        f"Manpower on Site: {manpower} personnel\n"
        f"Major Work Accomplished: {tasks_completed}\n"
        f"Safety Incidents / Issues / Delays: {issues}\n\n"
        f"Write a structured professional report with the following sections:\n"
        f"1. Executive Summary – what was accomplished today and overall progress\n"
        f"2. Detailed Activity Log – expand and professionalize the raw notes\n"
        f"3. Workforce & Weather Impact – analyze how weather and manpower affected progress\n"
        f"4. Safety & Compliance Status – comment on the incidents noted\n"
        f"5. Issues, Risks & Action Items – what needs to be addressed tomorrow\n"
        f"6. Recommendations – any efficiency or quality improvements for tomorrow\n\n"
        f"Be specific, professional, and use proper construction terminology."
    )
    return generate_or_raise(
        llama,
        prompt,
        "You are a senior Construction Project Manager writing official site documentation. Be thorough and professional.",
    )


def generate_report(llama: LlamaService, data: Dict[str, Any]) -> str:
    project_name = str(data.get("project_name", "")).strip()
    if not project_name:
        raise ValueError("Project name is required.")
    prompt = (
        "Create an audit-ready construction report using only the supplied facts. "
        "Do not invent progress, incidents, compliance scores, costs, or dates. "
        "Do not convert planned, pending, pre-construction, or unknown work into completed work. "
        "When information is unavailable, write 'Not provided'.\n\n"
        f"Project: {project_name}\n"
        f"Report type: {data.get('report_type', 'Executive Summary')}\n"
        f"Prepared by: {data.get('prepared_by', 'Not provided')}\n"
        f"Report date: {data.get('report_date', 'Not provided')}\n"
        f"Construction notes and known facts:\n{data.get('notes') or 'Not provided'}\n\n"
        "Use sections: Executive Summary, Progress and Work Status, Safety Findings, "
        "Compliance and Insurance Considerations, Risks, Required Actions, and Data Gaps."
    )
    return generate_or_raise(
        llama,
        prompt,
        "You are a careful construction reporting specialist. Never fabricate project facts.",
    )


def analyze_compliance(llama: LlamaService, data: Dict[str, Any]) -> Dict[str, Any]:
    phase = str(data.get("phase", "")).strip()
    standard = str(data.get("standard", "")).strip()
    notes = str(data.get("notes", "")).strip()
    if not phase or not standard:
        raise ValueError("Project phase and regulatory standard are required.")
    prompt = (
        f"Assess a construction audit for phase '{phase}' against '{standard}'.\n"
        f"Audit notes: {notes or 'No audit findings were supplied.'}\n\n"
        "Return one JSON object only with: score (integer 0-100), status "
        "(PASSING, WARNING, or NEEDS REVIEW), findings (array of objects with text and "
        "status PASS/FLAGGED/FAIL), and actions (plain text). Base conclusions only on "
        "the supplied notes. Missing evidence must lower confidence and be identified, "
        "not invented."
    )
    raw = generate_or_raise(
        llama,
        prompt,
        "You are a construction compliance assistant. Your output is advisory, not legal certification.",
    )
    result = extract_json_object(raw)
    if not result:
        return {
            "score": 0,
            "status": "NEEDS REVIEW",
            "findings": [{"text": "The AI response could not be validated as structured compliance data.", "status": "FLAGGED"}],
            "actions": raw,
        }
    result["score"] = max(0, min(100, int(result.get("score", 0))))
    result["status"] = str(result.get("status", "NEEDS REVIEW")).upper()
    result["findings"] = result.get("findings") if isinstance(result.get("findings"), list) else []
    result["actions"] = str(result.get("actions", "Professional review is required."))
    return result


def analyze_insurance(llama: LlamaService, data: Dict[str, Any]) -> Dict[str, Any]:
    event_type = str(data.get("event_type", "")).strip()
    description = str(data.get("description", "")).strip()
    try:
        impact = max(0.0, float(data.get("impact", 0)))
    except (TypeError, ValueError) as exc:
        raise ValueError("Estimated financial impact must be a number.") from exc
    if not event_type or not description:
        raise ValueError("Event type and incident description are required.")
    prompt = (
        f"Evaluate this construction insurance event. Event type: {event_type}. "
        f"Estimated financial impact: ${impact:,.2f}. Description: {description}\n\n"
        "Return one JSON object only with: risk_score (integer 0-100), severity, "
        "recommendation, and claim_document. The claim_document must summarize only "
        "provided facts and list evidence still required. Do not state that a claim is "
        "covered or denied and do not invent witnesses, dates, policy terms, or evidence."
    )
    raw = generate_or_raise(
        llama,
        prompt,
        "You are an advisory construction insurance risk assistant, not an insurer or attorney.",
    )
    result = extract_json_object(raw)
    if not result:
        return {
            "risk_score": 0,
            "severity": "Professional review required",
            "recommendation": raw,
            "claim_document": "A validated claim draft could not be generated. Preserve all incident evidence.",
        }
    result["risk_score"] = max(0, min(100, int(result.get("risk_score", 0))))
    result["severity"] = str(result.get("severity", "Professional review required"))
    result["recommendation"] = str(result.get("recommendation", "Notify the appropriate insurance professional."))
    result["claim_document"] = str(result.get("claim_document", "No claim draft was returned."))
    return result


def _normalize_color(value: Any) -> Tuple[int, int, int] | None:
    if not isinstance(value, (list, tuple)) or len(value) < 3:
        return None
    try:
        return tuple(max(0, min(255, int(component))) for component in value[:3])
    except (TypeError, ValueError):
        return None


def ai_theme(llama: LlamaService, prompt: str) -> Dict[str, Any] | None:
    if not prompt.strip():
        return None
    raw = generate_or_raise(
        llama,
        "Create an exterior color palette for this request: " + prompt + "\n"
        "Return JSON only with name and RGB arrays named wall, balcony, column, wood.",
        "You are an exterior color designer. Return valid JSON only.",
    )
    value = extract_json_object(raw)
    if not value:
        return None
    # LLMs commonly group palette channels beneath a ``colors`` object even
    # when asked for flat keys. Accept both valid shapes instead of silently
    # discarding an otherwise usable AI-generated palette.
    palette = value.get("colors") if isinstance(value.get("colors"), dict) else value
    colors = {name: _normalize_color(palette.get(name)) for name in ("wall", "balcony", "column", "wood")}
    if any(color is None for color in colors.values()):
        return None
    return {"name": str(value.get("name", "Custom AI Theme"))[:80], **colors}


def _apply_theme(image: Image.Image, palette: Dict[str, Any]) -> Image.Image:
    source = np.asarray(image.convert("RGB"), dtype=np.float32)
    result = source.copy()
    brightness = source.mean(axis=2)
    maximum = source.max(axis=2)
    minimum = source.min(axis=2)
    saturation = maximum - minimum
    masks = {
        "wall": (brightness >= 170) & (saturation < 80),
        "balcony": (brightness >= 75) & (brightness < 170) & (saturation < 75),
        "column": (brightness >= 145) & (brightness < 220) & (saturation < 45),
        "wood": (source[:, :, 0] > source[:, :, 2] * 1.12) & (source[:, :, 0] > source[:, :, 1] * 0.92),
    }
    alpha = 0.42
    for part, mask in masks.items():
        color = np.array(palette[part], dtype=np.float32)
        result[mask] = source[mask] * (1 - alpha) + color * alpha
    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), "RGB")


def generate_themes(llama: LlamaService, image_bytes: bytes, prompt: str = "") -> List[Dict[str, str]]:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError("The uploaded file is not a valid image.") from exc
    if image.width * image.height > 25_000_000:
        raise ValueError("Image dimensions are too large (maximum 25 megapixels).")

    palettes: List[Tuple[str, Dict[str, Any], str]] = []
    custom = ai_theme(llama, prompt) if prompt.strip() else None
    if custom:
        palettes.append((custom["name"], custom, "AI"))
    palettes.extend((name, value, "Default") for name, value in DEFAULT_THEMES.items())

    output = []
    request_id = uuid.uuid4().hex[:10]
    for index, (name, palette, source) in enumerate(palettes):
        filename = f"{request_id}_{index}.jpg"
        _apply_theme(image, palette).save(THEME_OUTPUT_DIR / filename, "JPEG", quality=92)
        output.append({"name": name, "image": f"/generated_themes/{filename}", "source": source})
    return output


def safety_samples(limit: int = 12) -> List[str]:
    if not PPE_IMAGES_DIR.exists():
        return []
    return sorted(
        path.name for path in PPE_IMAGES_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )[: max(1, min(limit, 100))]


def _read_labels(path: Path, width: int, height: int) -> List[Dict[str, Any]]:
    detections = []
    if not path.exists():
        return detections
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        try:
            class_id = int(float(parts[0]))
            center_x, center_y, box_width, box_height = map(float, parts[1:5])
        except ValueError:
            continue
        x1 = max(0, int((center_x - box_width / 2) * width))
        y1 = max(0, int((center_y - box_height / 2) * height))
        x2 = min(width - 1, int((center_x + box_width / 2) * width))
        y2 = min(height - 1, int((center_y + box_height / 2) * height))
        detections.append({"class_id": class_id, "name": PPE_CLASS_MAP.get(class_id, f"Class {class_id}"), "box": [x1, y1, x2, y2]})
    return detections


def _inside(box: Iterable[int], person_box: Iterable[int]) -> bool:
    x1, y1, x2, y2 = box
    px1, py1, px2, py2 = person_box
    center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
    return px1 <= center_x <= px2 and py1 <= center_y <= py2


def analyze_safety_sample(llama: LlamaService, filename: str) -> Dict[str, Any]:
    safe_name = Path(filename).name
    if safe_name != filename:
        raise ValueError("Invalid sample filename.")
    image_path = PPE_IMAGES_DIR / safe_name
    if not image_path.is_file():
        raise FileNotFoundError("Safety sample image was not found.")
    label_path = PPE_LABELS_DIR / f"{image_path.stem}.txt"
    image = Image.open(image_path).convert("RGB")
    detections = _read_labels(label_path, image.width, image.height)
    draw = ImageDraw.Draw(image)

    for detection in detections:
        violation = detection["name"].startswith("NO-")
        color = (220, 38, 38) if violation else (22, 163, 74)
        draw.rectangle(detection["box"], outline=color, width=3)
        draw.text((detection["box"][0] + 2, max(0, detection["box"][1] - 13)), detection["name"], fill=color)

    people = [item for item in detections if item["name"] == "Person"]
    equipment = [item for item in detections if item["name"] != "Person"]
    zones = ["Scaffolding Zone", "Excavation Zone", "Material Hoisting Zone", "Bricklaying Area"]
    workers = []
    for index, person in enumerate(people, start=1):
        assigned = [item["name"] for item in equipment if _inside(item["box"], person["box"])]
        violations = sorted({name for name in assigned if name.startswith("NO-")})
        ppe = sorted({name for name in assigned if not name.startswith("NO-")})
        status = "Violating" if violations else "Safe"
        workers.append({
            "id": index,
            "box": person["box"],
            "ppe": ppe,
            "violations": violations,
            "status": status,
            "zone": zones[(index - 1) % len(zones)],
            "behavior_analysis": "Dataset labels indicate " + (", ".join(violations) if violations else "no labelled PPE violation"),
        })

    violations_count = sum(len(worker["violations"]) for worker in workers)
    compliant_workers = sum(worker["status"] == "Safe" for worker in workers)
    total_workers = len(workers)
    compliance_score = round(compliant_workers / total_workers * 100) if total_workers else 100
    output_name = f"detected_{uuid.uuid4().hex[:8]}_{safe_name}"
    image.save(TEMP_DIR / output_name)

    summary = "; ".join(
        f"Worker {worker['id']}: {', '.join(worker['violations']) or 'no labelled violation'}"
        for worker in workers
    ) or "No person class was present in the dataset labels."
    try:
        recommendations = generate_or_raise(
            llama,
            "Provide concise corrective actions for these PPE dataset-label findings: " + summary,
            "You are a construction safety assistant. State that detections come from dataset labels and require human verification.",
        )
    except RuntimeError as exc:
        recommendations = str(exc)

    return {
        "mode": "dataset_ground_truth_demo",
        "notice": "Boxes are rendered from validation-dataset labels, not live model inference.",
        "processed_url": f"/temp/{output_name}",
        "stats": {
            "total_workers": total_workers,
            "violations_count": violations_count,
            "compliant_workers": compliant_workers,
            "compliance_score": compliance_score,
        },
        "workers": workers,
        "recommendations": recommendations,
    }


def match_uploaded_sample(filename: str, content: bytes) -> str | None:
    """Allow uploads only when they exactly match a labelled validation sample."""
    candidate = PPE_IMAGES_DIR / Path(filename).name
    if not candidate.is_file() or candidate.stat().st_size != len(content):
        return None
    if hashlib.sha256(candidate.read_bytes()).digest() != hashlib.sha256(content).digest():
        return None
    return candidate.name