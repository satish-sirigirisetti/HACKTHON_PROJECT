"""Lexical retrieval over structured career data; replaceable by vector search."""

import re
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database.models import Career, CareerSkill, LearningResource, Project, Skill
from backend.rag.chunking import chunk_text
from backend.rag.ingestion import ingest_document

STOP_WORDS = {
    "a", "an", "and", "are", "about", "can", "for", "from", "how", "i", "in", "is",
    "it", "me", "my", "of", "on", "or", "should", "the", "to", "what", "which", "with",
}
RETRIEVAL_METHOD = "Keyword relevance over the CareerAI career, skills, project, and resource catalog."


@dataclass(frozen=True)
class RetrievedContext:
    title: str
    source_type: str
    text: str
    url: str | None = None
    score: float = 0.0


def retrieve_context(session: Session, query: str, limit: int = 5) -> list[RetrievedContext]:
    """Rank catalog passages by query-term overlap; no result is fabricated."""
    terms = _terms(query)
    if not terms:
        return []
    documents: list[RetrievedContext] = []
    careers = session.scalars(select(Career).order_by(Career.name)).all()
    for career in careers:
        skills = session.execute(
            select(Skill.name)
            .join(CareerSkill, CareerSkill.skill_id == Skill.id)
            .where(CareerSkill.career_id == career.id, CareerSkill.required.is_(True))
            .order_by(Skill.name)
        ).scalars().all()
        text = f"{career.name}. Category: {career.category}. {career.description} Required skills: {', '.join(skills)}."
        documents.append(RetrievedContext(career.name, "career profile", text))

    for skill in session.scalars(select(Skill).order_by(Skill.name)):
        text = f"{skill.name}. Category: {skill.category}. {skill.description or ''}"
        documents.append(RetrievedContext(skill.name, "skill catalog", text))

    for resource in session.scalars(select(LearningResource).order_by(LearningResource.title)):
        text = f"{resource.title}. Provider: {resource.provider}. Type: {resource.resource_type}. Skill: {resource.skill_name}."
        documents.append(
            RetrievedContext(resource.title, "learning resource", text, resource.url)
        )

    for project in session.scalars(select(Project).order_by(Project.title)):
        text = f"{project.title}. {project.description} Skills practiced: {', '.join(project.skill_names)}."
        documents.append(RetrievedContext(project.title, "project idea", text, project.source_url))

    documents_dir = Path(__file__).parent / "documents"
    for path in sorted(documents_dir.glob("*.md")):
        for index, chunk in enumerate(chunk_text(ingest_document(path)), start=1):
            documents.append(
                RetrievedContext(f"{path.stem.replace('-', ' ').title()} · section {index}", "career guidance document", chunk)
            )

    ranked: list[RetrievedContext] = []
    for document in documents:
        document_terms = _terms(document.text)
        overlap = len(terms & document_terms)
        if overlap:
            learning_intent = bool(terms & {"learn", "learning", "tutorial", "course", "resource"})
            intent_boost = 0.2 if learning_intent and document.source_type == "learning resource" else 0.0
            ranked.append(
                RetrievedContext(
                    title=document.title,
                    source_type=document.source_type,
                    text=document.text,
                    url=document.url,
                    score=overlap / len(terms) + intent_boost,
                )
            )
    return sorted(ranked, key=lambda item: (-item.score, item.title.casefold()))[: max(1, limit)]


def _terms(text: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9+#.]{2,}", text.casefold()) if term not in STOP_WORDS}