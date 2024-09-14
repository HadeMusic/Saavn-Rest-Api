import aiohttp
from typing import Any , Literal , List , Dict

class Silder:
    async def _request(self , method : Literal["GET" , "POST"] , url : str , *args : Any , **kwargs : Any):
        async with aiohttp.ClientSession() as session:
            async with session.request(method=method , url=url , *args , **kwargs) as resp:
                return await resp.json()
            
    @staticmethod
    def format_track(data : Dict[str , Any]) -> Dict[str , Any]:
        track = dict()
        track['identifier'] =  data['url']
        track['uri'] = data['url']
        info = data['tit_art'].split('-')
        track['title'] = info[-1] if len(info) >= 2 else ''
        track['author'] = ','.join([n.replace(',' , '') for n in info[:-1]]) if len(info) >= 2 else ''
        track['length'] = int(data['duration']) * 1000
        track['artworkUrl'] = None
        track['sourceName'] = 'sliderkz'
        return track     
    
    async def search(self , query : str) ->  List[Any]:
        resp = await self._request(method="GET" , url="https://hayqbhgr.slider.kz/vk_auth.php?q={}".format(query))
        tracks = []
        audios = resp.get('audios' , {})
        for data in audios.get("", []):
            track = self.format_track(data)
            tracks.append(track)
        return tracks    
        
               

