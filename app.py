from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from saavn import Saavn
import time
from starlette.middleware.base import BaseHTTPMiddleware
from mangum import Mangum
saavn = Saavn()



def get_client(request: Request):
    return saavn


class AiohttpSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
        


app = FastAPI(
     debug=True, title="Saavn Rest Api", description="Saavn Rest Api", version="0.0.1"
)

app.add_middleware(AiohttpSessionMiddleware)

@app.get("/saavn/search/query={query}")
async def get_search(query: str, saavn: Saavn = Depends(get_client)) -> JSONResponse:
    search = await saavn.get_search(query)
    return JSONResponse(content=search, status_code=200)


@app.get("/saavn/track/id={id}")
async def get_track(id: str, saavn: Saavn = Depends(get_client)) -> JSONResponse:
    tracks = await saavn.get_track(id)
    return JSONResponse(content=tracks, status_code=200)


@app.get("/saavn/album/id={id}")
async def get_album(id: str, saavn: Saavn = Depends(get_client)) -> JSONResponse:
    album = await saavn.get_album(id)
    return JSONResponse(content=album, status_code=200)


@app.get("/saavn/playlist/id={id}")
async def get_playlist(id: str, saavn: Saavn = Depends(get_client)) -> JSONResponse:
    playlist = await saavn.get_playlist(id)
    return JSONResponse(content=playlist, status_code=200)


@app.get("/saavn/artist/id={id}")
async def get_artist(id: str, saavn: Saavn = Depends(get_client)) -> JSONResponse:
    artist = await saavn.get_artist(id)
    return JSONResponse(content=artist, status_code=200)


@app.get("/saavn/autocomplete/")
async def get_autocomplete(
    query: str, saavn: Saavn = Depends(get_client)
) -> JSONResponse:
    autocomplete = await saavn.get_autocomplete(query)
    return JSONResponse(content=autocomplete, status_code=200)

@app.get('/sliderkz/search/query={query}')
async def slider_search(query : str) -> JSONResponse:
    return await Silder().search(query)

handler = Mangum(app, lifespan="off")
