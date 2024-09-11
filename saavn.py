from typing import Dict , Any , List , Literal , Union
import aiohttp
import orjson as json
from contextlib import suppress

class Saavn:
    session : Union[aiohttp.ClientSession , None]
    
    async def setup(self) -> None:
        self.session = aiohttp.ClientSession()
    
    async def close(self) -> None:
        if self.session:
            await self.session.close()
    
    async def _request(self , method : Literal["GET" , "POST"] , url : str , *args : Any , **kwargs : Any):
        async with self.session.request(method=method , url=url , *args , **kwargs) as resp:
            return await resp.text()
                  
        
    def cleanstring(self , text : Union[str , None]) -> str:
        if text is not None:
            return text.replace("&quot;" , "").replace("&amp;" , "")
        return text

    def format_track(self , data : Dict[str , Any]) -> Dict[str , Any]:
        track = dict()
        track['identifier'] = data['id']
        track['title'] = self.cleanstring(data['song'])
        track['author'] = self.cleanstring(data.get('singers' , None) or data.get('primary_artists' , None))
        track['length'] = int(data['duration']) * 1000
        track['uri'] = data['perma_url']
        track['artworkUrl'] = data.get('image').replace('150x150' , '500x500') if data.get('image' , None) else None 
        track['albumName'] = data.get('album' , None)
        track['albumUrl'] = data.get('album_url' , None)
        track['artistUrl'] = None
        track['artistArtworkUrl'] = None
        if data.get('media_preview_url' , None):
            track['previewUrl'] = data['media_preview_url']
        else:
            if data.get('vlink' , None):
                track['previewUrl'] = data['vlink']
            else:
                track['previewUrl'] = None
        return track            


    def format_song(self , data : Dict[str , Any]) -> Dict[str , Any]:
        song = dict()
        song['identifier'] = data['id']
        song['title'] = self.cleanstring(data['title'])
        song['author'] = self.cleanstring(data['more_info']['music'])
        song['length'] = int(data['more_info']['duration']) * 1000
        song['uri'] = data['perma_url']
        song['artworkUrl'] = data.get('image').replace('150x150' , '500x500') if data.get('image' , None) else None 
        song['albumName'] = data.get('more_info' , {}).get('album' , None)
        song['albumUrl'] = data.get('more_info' , {}).get('album_url' , None)
        
        if data['more_info']['artistMap'].get('primary_artists' , []):
            song['artistUrl'] = data['more_info']['artistMap']['primary_artists'][0]['perma_url']
            if data['more_info']['artistMap']['primary_artists'][0].get('image') != "":
                song['artistArtworkUrl'] = data['more_info']['artistMap']['primary_artists'][0]['image']
            else:
                song['artistArtworkUrl'] = None    
        else:
            song['artistUrl'] = None
            song['artistArtworkUrl'] = None
                
        if data.get('more_info' , {}).get('vlink' , None):
            song['previewUrl'] = data['more_info']['vlink']
        else:
            song['previewUrl'] = None
        return song        

    def format_album(self , data : Dict[str , Any]) -> Dict[str , Any]:
        album = dict()
        album['title'] = data['title']
        album['image'] = data.get('image').replace('150x150' , '500x500') if data.get('image' , None) else None 
        album['url'] = data['perma_url']
        album['track_count'] = int(data['more_info']['song_count'])
        album['songs'] = [self.format_song(song) for song in data.get('list',[])]
        if len(album['songs']) > 0:
            album['author'] = album['songs'][0]['author']
        else:
            album['author'] = data['subtitle']
        
        if data['id'] == "":
            album['songs'] = []
            album['track_count'] = 0
        else:        
            album['id'] = data['id']
                
        return album
    
    

    def format_artist(self , data : Dict[str , Any]) -> Dict[str , Any]:
        artist = dict()
        artist['title'] = data['name']
        artist['image'] = data.get('image').replace('150x150' , '500x500') if data.get('image' , None) else None 
        artist['url'] = data['urls']['overview']
        artist['songs'] = [self.format_song(song) for song in data.get('topSongs',[])]
        if data['artistId'] == "":
            artist['songs'] = []
        else:
            artist['id'] = data['artistId']    
        artist['track_count'] = len(artist['songs'])
        return artist
    

    def format_playlist(self , data : Dict[str , Any]) -> Dict[str , Any]:
        playlist = dict()
        playlist['title'] = data['title'].replace("&quot;" , "")
        if data.get('more_info', {}).get('firstname') != "":
            playlist['author'] = data['more_info']['firstname'] 
        else:    
            playlist['author'] = data['more_info']['username']
        playlist['image'] = data.get('image').replace('150x150' , '500x500') if data.get('image' , None) else None 
        playlist['url'] = data['perma_url']
        playlist['songs'] = [self.format_song(song) for song in data.get('list',[])]
        if data['id'] == "":
            playlist['songs'] = []
        else:
            playlist['id'] = data['id']    
        playlist['track_count'] = len(playlist['songs'])
        return playlist
    

    async def get_search(self , query : str) -> Any:
        data = await self._request(method="GET" , url=f"https://www.jiosaavn.com/api.php?__call=search.getResults&_format=json&_marker=0&cc=in&includeMetaTags=1&q={query}")
        response : Dict[str , List[Any]]= {'results': []}
        with suppress(json.JSONDecodeError):
            data = json.loads(data)
            for d in data.get('results' , []):
                track = self.format_track(d)
                response['results'].append(track)
        return response
           
    async def get_track(self , id : int) -> Dict[str , List[Any]]:
        resp = await self._request(method="GET" , url=f"https://www.jiosaavn.com/api.php?__call=webapi.get&api_version=4&_format=json&_marker=0&ctx=web6dot0&token={id}&type=song")
        songs = []
        with suppress(json.JSONDecodeError):
            data = json.loads(resp)
            songs = [self.format_song(song) for song in data.get('songs' , [])]
        return {'songs' : songs}
                    

    async def get_album(self , id : int) -> Dict[str , Any]:
        resp = await self._request(method="GET" , url=f"https://www.jiosaavn.com/api.php?__call=webapi.get&api_version=4&_format=json&_marker=0&ctx=web6dot0&token={id}&type=album")
        with suppress(json.JSONDecodeError):
            data = json.loads(resp)
            return self.format_album(data)
        
    async def get_artist(self , id : int) -> Dict[str , Any]:
        resp = await self._request(method="GET" , url=f"https://www.jiosaavn.com/api.php?__call=webapi.get&api_version=4&_format=json&_marker=0&ctx=web6dot0&token={id}&type=artist")
        with suppress(json.JSONDecodeError):
            data = json.loads(resp)    
            return self.format_artist(data)
        

    async def get_playlist(self , id : int) -> Any:
        resp = await self._request(method="GET" , url=f"https://www.jiosaavn.com/api.php?__call=webapi.get&api_version=4&_format=json&_marker=0&ctx=web6dot0&token={id}&type=playlist&n=10000")
        with suppress(json.JSONDecodeError):
                data = json.loads(resp)    
                return self.format_playlist(data)

    async def get_autocomplete(self , query : str) -> Any:
        resp = await self._request(method="GET" , url=f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&api_version=4&_format=json&_marker=0&ctx=web6dot0&query={query}")
        with suppress(json.JSONDecodeError):
            data = json.loads(resp)
            data.pop('shows' , None)
            return data
    
    async def get_media(self , track_id : str) -> str:
        pass
            
                
            
    

                                     
                
            
