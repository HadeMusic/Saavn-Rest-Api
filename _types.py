from pydantic import BaseModel
from typing import List , Optional

class SaavnTrack(BaseModel):
    identifier : str
    title : str
    author : str
    length : int
    uri : str
    artworkUrl : Optional[str]
    albumName : Optional[str]
    albumUrl : Optional[str]
    artistUrl : Optional[str]
    artistArtworkUrl : Optional[str]
    previewUrl : Optional[str] 
    

class SearchResponse(BaseModel):
    results : List[SaavnTrack]
    
    