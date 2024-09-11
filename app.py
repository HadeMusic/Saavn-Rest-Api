from fastapi import FastAPI  , Depends , Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from saavn import Saavn
import asyncio
from _types import SearchResponse

try:
    import uvloop # type: ignore
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass    



@asynccontextmanager
async def get_session(app : FastAPI):
    app.state.saavn = Saavn()
    try:
        await app.state.saavn.setup() 
        yield
    finally:
        await app.state.saavn.close() 
        

def get_client(request : Request) -> Saavn:
    return request.app.state.saavn        
    

app = FastAPI(debug=True  , lifespan=get_session , title="Saavn Rest Api" , description="Saavn Rest Api" , version="0.0.1")


@app.get('/saavn/search/query={query}')
async def get_search(query : str , saavn : Saavn = Depends(get_client)) -> SearchResponse:
    """Returns serach results from Saavan API.

    Args:
        `query` (str): Song that you want to serach
        
    Returns:
        **JSONResponse** : A dict containing the search results
    """
    search = await saavn.get_search(query)
    return JSONResponse(content=search , status_code=200)

@app.get('/saavn/track/id={id}')
async def get_track(id :  str , saavn : Saavn = Depends(get_client) ) -> JSONResponse:
    tracks = await saavn.get_track(id)
    return JSONResponse(content=tracks , status_code=200)



@app.get('/saavn/album/id={id}')
async def get_album(id : str , saavn : Saavn = Depends(get_client) ) -> JSONResponse:
    album = await saavn.get_album(id)
    return JSONResponse(content=album , status_code=200)



@app.get('/saavn/playlist/id={id}')
async def get_playlist(id : str , saavn : Saavn = Depends(get_client) ) ->JSONResponse:
    playlist = await saavn.get_playlist(id)
    return JSONResponse(content=playlist , status_code=200)

@app.get('/saavn/artist/id={id}')
async def get_artist(id : str, saavn : Saavn = Depends(get_client) ) -> JSONResponse:
    artist = await saavn.get_artist(id)
    return JSONResponse(content=artist , status_code=200)

@app.get('/saavn/autocomplete/')
async def get_autocomplete( query : str , saavn : Saavn = Depends(get_client) ) -> JSONResponse:
    autocomplete = await saavn.get_autocomplete(query)
    return JSONResponse(content=autocomplete , status_code=200)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run('app:app' , host='0.0.0.0' , port=8000 , log_level=20 , reload=True)
    


