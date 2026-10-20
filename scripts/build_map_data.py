"""Build pinned, public-domain map fixtures. Run with Python 3; network needed only here."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'ca96624a56bd078437bca8184e78163e5039ad19'
BASE = f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{COMMIT}/geojson/'
CITIES = [
 ('cn-beijing','Beijing','北京','Mainland China','Beijing'),
 ('cn-shanghai','Shanghai','上海','Mainland China','Shanghai'),
 ('cn-hangzhou','Hangzhou','杭州','Mainland China','Hangzhou'),
 ('cn-nanjing','Nanjing','南京','Mainland China','Nanjing'),
 ('cn-chengdu','Chengdu','成都','Mainland China','Chengdu'),
 ('cn-chongqing','Chongqing','重庆','Mainland China','Chongqing'),
 ('cn-xian',"Xi’an",'西安','Mainland China','Xian'),
 ('cn-guangzhou','Guangzhou','广州','Mainland China','Guangzhou'),
 ('cn-shenzhen','Shenzhen','深圳','Mainland China','Shenzhen'),
 ('hk-hong-kong','Hong Kong','香港','Hong Kong and Macau','Hong Kong'),
 ('mo-macau','Macau','澳门','Hong Kong and Macau','Macau'),
 ('tw-taipei','Taipei','台北','Taiwan','Taipei'),
 ('tw-kaohsiung','Kaohsiung','高雄','Taiwan','Kaohsiung'),
 ('jp-tokyo','Tokyo','東京','Japan','Tokyo'),
 ('jp-osaka','Osaka','大阪','Japan','Ōsaka'),
 ('jp-kyoto','Kyoto','京都','Japan','Kyoto'),
 ('jp-sapporo','Sapporo','札幌','Japan','Sapporo'),
 ('jp-fukuoka','Fukuoka','福岡','Japan','Fukuoka'),
 ('jp-naha','Naha','那覇','Japan','Naha'),
]

def build():
    sources=[]; loaded={}
    for name in ['ne_50m_land','ne_10m_populated_places']:
        url=BASE+name+'.geojson'
        raw=urlopen(Request(url,headers={'User-Agent':'AILT9019-map-build'}),timeout=60).read()
        loaded[name]=json.loads(raw)
        sources.append({'name':name,'url':url,'sha256':hashlib.sha256(raw).hexdigest()})
    cities=[]
    for city_id,name,local,region,source_name in CITIES:
        matches=[f for f in loaded['ne_10m_populated_places']['features'] if f['properties']['NAME']==source_name]
        assert len(matches)==1,source_name
        feature=matches[0];lon,lat=feature['geometry']['coordinates']
        cities.append(dict(id=city_id,name=name,local_name=local,region=region,longitude=lon,latitude=lat,source_ne_id=feature['properties']['NE_ID']))
    features=[]
    for feature in loaded['ne_50m_land']['features']:
        geometry=feature['geometry']
        polygons=[geometry['coordinates']] if geometry['type']=='Polygon' else geometry['coordinates']
        for polygon in polygons:
            xs=[p[0] for p in polygon[0]]; ys=[p[1] for p in polygon[0]]
            if max(xs)<88 or min(xs)>160 or max(ys)<5 or min(ys)>60: continue
            features.append({'type':'Feature','properties':{},'geometry':{'type':'Polygon','coordinates':polygon}})
    land={'type':'FeatureCollection','features':features}
    output=ROOT/'data/map';output.mkdir(parents=True,exist_ok=True)
    (output/'land.geojson').write_text(json.dumps(land,separators=(',',':'))+'\n')
    (ROOT/'data/cities.json').write_text(json.dumps(cities,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'data/SOURCES.json').write_text(json.dumps({'licence':'Public domain','licence_url':'https://www.naturalearthdata.com/about/terms-of-use/','accessed':'2026-10-01','source_commit':COMMIT,'sources':sources,'transformations':['Land: retain polygons whose bounding boxes intersect 88–160°E, 5–60°N; remove unused properties. Coordinates unchanged.','Cities: select 19 named points; retain coordinates and NE_ID; add stable app IDs, display translations and UI group labels.'],'limitations':['1:50m land outlines for regional browsing; tiny islands may still be absent.','City markers indicate approximate centres, not routes, borders or proof of a visit.','UI groups and IDs are application organisation, not administrative-boundary data.']},indent=2)+'\n')
    print(f'Built {len(cities)} cities and {len(land["features"])} land features')

if __name__=='__main__': build()
