from asyncio import sleep
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from decoRouter import Router
from modules.utils import timestamp, generate_id
from todo import Todo, all_todo, get_todo, update_todo, save_todo, delete_todo
from config import TEMPLATES

router = Router()

@router.get('/todos')
async def todo_index(request:Request):
    todos = all_todo()
    try:
        return TEMPLATES.TemplateResponse('todo/todo_index.html', 
            {'request': request, 'todos': todos, 'exception':None})
    except Exception as ex:
        return TEMPLATES.TemplateResponse('todo/todo_index.html', 
            {'request': request, 'todos': todos, 'exception': str(ex)})
    finally: del todos



@router.get('/done_todos')
async def completed_todos(request:Request):
    todos = all_todo()
    try:
        return TEMPLATES.TemplateResponse('todo/doneTodos.html', 
            {'request': request, 'todos': todos })
    finally: del todos


@router.post('/done_todo/{id}')
async def done_todo(request:Request):
    id = request.path_params.get('id')
    todo = None
    async with request.form() as form:
        done_signal = form.get('done_todo')
    if done_signal == 'on':   
        todo:Todo = Todo(**get_todo(id=id)[0])
        todo.done = True
        update_todo(data=todo.model_dump())        
    todos = all_todo()
    try:
        return TEMPLATES.TemplateResponse('todo/todos.html', 
            {'request': request, 'todos': todos, 'exception':None})
    except Exception as ex:
        return TEMPLATES.TemplateResponse('todo/todos.html', 
            {'request': request, 'todos': todos, 'exception': str(ex)})
    finally: 
        del todos
        del todo
        del id
        del done_signal




@router.post('/add_todo')
async def add_todo(request:Request):  
    data = {

        "id": generate_id(name='To Do'),
        "date": timestamp(),
        "description": "",
        "priority": 0,

    }  
    async with request.form() as form:
        data['description'] = form.get('todo')  
        data['priority'] = form.get('priority') 
    if len(data.get('description')) > 2:       
        todo:Todo = Todo(**data)
        save_todo(data=todo.model_dump())
    todos = all_todo()
    try:
        return TEMPLATES.TemplateResponse('todo/todos.html', 
            {'request': request, 'todos': todos, 'exception':None})
    except Exception as ex:
        return TEMPLATES.TemplateResponse('todo/todos.html', 
            {'request': request, 'todos': todos, 'exception': str(ex)})
    finally: 
        del todos
        del data


@router.delete('/delete_todo/{id}')
async def remove_todo(request:Request):
    id = request.path_params.get('id')
    delete_todo(id=id)    
    todos = all_todo()
    try:
        return TEMPLATES.TemplateResponse('todo/todos.html', 
            {'request': request, 'todos': todos, 'exception':None})
    except Exception as ex:
        return TEMPLATES.TemplateResponse('todo/todos.html', 
            {'request': request, 'todos': todos, 'exception': str(ex)})
    finally: 
        del todos
        del id


@router.post('/update_priority/{id}')
async def update_priority(request:Request):
    id = request.path_params.get('id')
    todo:Todo = Todo(**get_todo(id=id)[0])
    todo.priority += 1
    try:
        update_todo(data=todo.model_dump())     
        return HTMLResponse(f"{todo.priority}") 
    finally:
        del id
        del todo 



@router.get('/todo_list')
async def todo_list(request:Request):
    todos = all_todo()
    todo_list = [ todo.get('description') for todo in todos if not todo.get('done')]    
    try:
        return TEMPLATES.TemplateResponse('todo/todoList.html', 
            {'request': request, 'todo_list': todo_list, 'exception':None})
    finally: del todos






