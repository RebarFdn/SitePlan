
import os
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.background import BackgroundTask
from decoRouter import Router
from PIL import Image
from io import BytesIO
from pathlib import Path
from config import DROPBOX_PATH, TEMPLATES
from modules.utils import timestamp, generate_id
from modules.dropbox import Dropbox


router = Router()

@router.get('/dropbox')
async def dropbox(request:Request):
    time_id = (timestamp(), generate_id(name= 'd b'))   
    dropbox = Dropbox() 

    try:
        return TEMPLATES.TemplateResponse('/dropbox/index.html', 
            {'request': request, 'boxindex': dropbox.contents, 'box': dropbox })
    except Exception as ex:
        return TEMPLATES.TemplateResponse('/dropbox/exception.html', 
            {'request': request, 'exception': str(ex)})
    finally:         
        del time_id


async def handle_image_upload(profile_path:str, file_name:str, file_contents)->None:
    """_summary_

    Args:
        profile_path (str): _description_
        file_contents (Image): _description_
    """
    if '.jpg' in file_name or '.png' in file_name:
        img = Image.open(BytesIO(file_contents))
        img.save(profile_path)
        img.close()
    elif '.txt' in file_name:
        with open(profile_path, 'w') as file:
            file.write(file_contents)
    else:
        with open(profile_path, 'wb') as file:
            file.write(file_contents)
    



@router.post('/dropbox')
async def upload_dropbox_item(request:Request)->RedirectResponse:
    async with request.form() as form:
        filename = form["content"].filename
        contents = await form["content"].read()
    profile_path = Path.joinpath(DROPBOX_PATH, filename)    
    task = BackgroundTask(handle_image_upload, profile_path, filename, contents)        
    return RedirectResponse(url="/dropbox", status_code=302, background=task)



@router.delete('/dropbox/{item}')
async def delete_dropbox_item(request:Request)->RedirectResponse:
    item = request.path_params.get('item')
    file_path = Path.joinpath(DROPBOX_PATH, item)
    os.remove(file_path) 
    return RedirectResponse(url="/dropbox", status_code=303)
