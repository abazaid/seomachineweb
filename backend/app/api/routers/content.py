from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.content import ContentItem, ContentVersion
from app.models.user import User
from app.schemas.content import ContentActionRequest, ContentCreateRequest, ContentOut, ContentVersionOut
from app.services.content_research_service import generate_research_brief


router = APIRouter(prefix='/content', tags=['content'])


def _save_version(db: Session, item: ContentItem, stage: str, body: str, user_id: int) -> None:
    db.add(
        ContentVersion(
            content_item_id=item.id,
            version_number=item.current_version,
            stage=stage,
            body=body,
            created_by_user_id=user_id,
        )
    )


@router.post('/brief', response_model=ContentOut)
def create_research_brief(
    payload: ContentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    brief = generate_research_brief(keyword=payload.keyword, title=payload.title)

    item = ContentItem(
        keyword=payload.keyword,
        title=payload.title,
        status='research',
        current_version=1,
        latest_body=brief,
        created_by_user_id=current_user.id,
    )
    db.add(item)
    db.flush()

    _save_version(db, item, 'research', brief, current_user.id)
    db.commit()
    db.refresh(item)
    return item


@router.post('/{content_id}/draft', response_model=ContentOut)
def generate_draft(
    content_id: int,
    payload: ContentActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Content item not found')

    item.current_version += 1
    item.status = 'draft'
    item.latest_body = (
        f"# {item.title}\n\n"
        f"????? ????? ???: {item.keyword}\n\n"
        '## ?????\n???? ??? ????? ?????? ?????? ??????? ???? ????????? ?????.\n\n'
        '## ?????? ????????\n- ???????? ??? ???????\n- ???? ??????? ?????????\n- ????? ???? ????? ???????\n\n'
        f"## ???????\n{payload.notes or '?? ???? ??????? ??????'}\n"
    )

    _save_version(db, item, 'draft', item.latest_body, current_user.id)
    db.commit()
    db.refresh(item)
    return item


@router.post('/{content_id}/optimize', response_model=ContentOut)
def optimize_content(
    content_id: int,
    payload: ContentActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(ContentItem).filter(ContentItem.id == content_id).first()
    if not item:
        raise HTTPException(status_code=404, detail='Content item not found')

    base = item.latest_body or ''
    item.current_version += 1
    item.status = 'optimized'
    item.latest_body = (
        f"{base}\n\n"
        '## SEO Optimization Checklist\n'
        '- ?? ????? ?????? ????????? ?? ???????\n'
        '- ?? ????? ???????? ??????? H2/H3\n'
        '- ?? ????? CTA ????\n'
        '- ?? ?????? ????? ??????\n'
        f"- ??????? ????? ??????: {payload.notes or '?? ????'}\n"
    )

    _save_version(db, item, 'optimized', item.latest_body, current_user.id)
    db.commit()
    db.refresh(item)
    return item


@router.get('', response_model=list[ContentOut])
def list_content(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return db.query(ContentItem).order_by(ContentItem.updated_at.desc()).all()


@router.get('/{content_id}/versions', response_model=list[ContentVersionOut])
def list_versions(
    content_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return (
        db.query(ContentVersion)
        .filter(ContentVersion.content_item_id == content_id)
        .order_by(ContentVersion.version_number.asc())
        .all()
    )
