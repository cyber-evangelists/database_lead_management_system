from fastapi import APIRouter,Request

router=APIRouter()



@router.get("/register",response_class=HTMLResponse)
def register_template(request:Request):
    with open(path.join(pth, "templates/register.html")) as f:
        return HTMLResponse(content=f.read())