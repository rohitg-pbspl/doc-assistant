from typing import Annotated

from fastapi import Depends, Header, HTTPException, status


def get_current_user(x_user: Annotated[str | None, Header()] = None) -> str:
    # Stand-in for real auth; later only this function changes (JWT).
    if not x_user or not x_user.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-User header"
        )
    return x_user.strip()


CurrentUser = Annotated[str, Depends(get_current_user)]
