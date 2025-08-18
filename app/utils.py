import random
import re
import unicodedata
from typing import Optional, Dict, Union
from sqlalchemy import func, select
from .models import BaseLayer, Condiment, Mixin, Seasoning, Shell
from sqlalchemy.orm import Session


def fetch_random(model, session: Session):
    """Fetch a random instance of the given model."""
    count = session.scalar(select(func.count()).select_from(model))
    if count:
        offset = random.randint(0, count - 1)
        stmt = select(model).offset(offset).limit(1)
        return session.scalar(stmt)
    return None


def fetch_random_ingredients(session: Session) -> Dict[str, Optional[Union[BaseLayer, Condiment, Mixin, Seasoning, Shell]]]:
    """Fetch random ingredients for a taco."""
    return {
        'seasoning': fetch_random(Seasoning, session),
        'condiment': fetch_random(Condiment, session),
        'mixin': fetch_random(Mixin, session),
        'base_layer': fetch_random(BaseLayer, session),
        'shell': fetch_random(Shell, session)
    }


def slugify(value: str) -> str:
    """Convert a string to a URL-friendly slug."""
    if not isinstance(value, str):
        value = str(value)
    
    # Normalize unicode characters
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    
    # Remove non-alphanumeric characters and convert to lowercase
    value = re.sub(r'[^\w\s-]', '', value.strip().lower())
    
    # Replace spaces and hyphens with underscores
    return re.sub(r'[-\s]+', '_', value)