import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ApiRepository,ApiError,requestJSON} from '../app/repository.mjs';

const cities=JSON.parse(readFileSync(new URL('../data/cities.json',import.meta.url)));
const seed=JSON.parse(readFileSync(new URL('../data/demo-trips.json',import.meta.url)));
const trip=seed[0];

function stubFetch(handler){
  const calls=[];
  const original=globalThis.fetch;
  globalThis.fetch=async (url,options={})=>{calls.push({url,options});return handler(url,options);};
  return {calls,restore(){globalThis.fetch=original;}};
}

test('ApiRepository.create posts metadata and validates the response',async ()=>{
  const created={...trip,id:'server-id',title:'A new memory'};
  const stub=stubFetch(async ()=>({ok:true,status:201,json:async()=>created}));
  try {
    const result=await new ApiRepository(cities).create({city_id:'jp-osaka',trip_date:'2026-05-16',title:'A new memory',notes:'Notes'});
    assert.equal(result.id,'server-id');
    assert.equal(stub.calls[0].url,'/api/trips');
    assert.equal(stub.calls[0].options.method,'POST');
    assert.equal(stub.calls[0].options.headers['Content-Type'],'application/json');
    assert.deepEqual(JSON.parse(stub.calls[0].options.body),{city_id:'jp-osaka',trip_date:'2026-05-16',title:'A new memory',notes:'Notes'});
  } finally {stub.restore();}
});

test('ApiRepository.edit patches only the supplied fields and encodes the ID',async ()=>{
  const stub=stubFetch(async ()=>({ok:true,status:200,json:async()=>({...trip,memory_text:'Edited'})}));
  try {
    const result=await new ApiRepository(cities).edit('id with space',{memory_text:'Edited'});
    assert.equal(result.memory_text,'Edited');
    assert.equal(stub.calls[0].url,'/api/trips/id%20with%20space');
    assert.equal(stub.calls[0].options.method,'PATCH');
    assert.deepEqual(JSON.parse(stub.calls[0].options.body),{memory_text:'Edited'});
  } finally {stub.restore();}
});

test('ApiRepository.remove accepts an empty 204 response',async ()=>{
  const stub=stubFetch(async ()=>({ok:true,status:204}));
  try {
    assert.equal(await new ApiRepository(cities).remove('trip-id'),null);
    assert.equal(stub.calls[0].options.method,'DELETE');
  } finally {stub.restore();}
});

test('ApiRepository.uploadPhoto sends multipart without a manual content type',async ()=>{
  const photo={id:'photo-id',url:'/media/photo-id.jpg',alt:'A view',width:800,height:600};
  const stub=stubFetch(async ()=>({ok:true,status:201,json:async()=>photo}));
  try {
    const file=new Blob(['fake-bytes'],{type:'image/jpeg'});
    const result=await new ApiRepository(cities).uploadPhoto('trip-id',file,{alt:'A view'});
    assert.equal(result.url,photo.url);
    assert.equal(stub.calls[0].url,'/api/trips/trip-id/photos');
    assert.equal(stub.calls[0].options.method,'POST');
    assert.equal(stub.calls[0].options.headers,undefined);
    assert.ok(stub.calls[0].options.body instanceof FormData);
    assert.equal(stub.calls[0].options.body.get('alt'),'A view');
  } finally {stub.restore();}
});

test('ApiRepository.requestMemory sends the explicit confirmation',async ()=>{
  const stub=stubFetch(async ()=>({ok:true,status:200,json:async()=>({status:'draft',title:'Draft',text:'Text'})}));
  try {
    const result=await new ApiRepository(cities).requestMemory('trip-id',{confirmed:true});
    assert.equal(result.status,'draft');
    assert.equal(stub.calls[0].url,'/api/trips/trip-id/memory');
    assert.deepEqual(JSON.parse(stub.calls[0].options.body),{confirmed:true});
  } finally {stub.restore();}
});

test('the error envelope becomes a typed ApiError without losing the status',async ()=>{
  const stub=stubFetch(async ()=>({ok:false,status:422,json:async()=>({error:{code:'validation_error',message:'trip_date must be real',details:[{loc:'body.trip_date'}]}})}));
  try {
    await assert.rejects(
      () => new ApiRepository(cities).edit('trip-id',{trip_date:'2026-02-31'}),
      error => error instanceof ApiError && error.status===422 && error.code==='validation_error' && /trip_date/.test(error.message) && error.details.length===1
    );
  } finally {stub.restore();}
});

test('a failed read still reports the status and never fabricates trips',async ()=>{
  const stub=stubFetch(async ()=>({ok:false,status:503}));
  try {
    await assert.rejects(()=>new ApiRepository(cities).list(),error=>error instanceof ApiError && error.status===503 && /503/.test(error.message));
  } finally {stub.restore();}
});

test('an aborted request is reported as a timeout',async ()=>{
  const stub=stubFetch(async ()=>{const error=new Error('aborted');error.name='AbortError';throw error;});
  try {
    await assert.rejects(()=>requestJSON('/api/trips'),error=>error instanceof ApiError && error.code==='timeout');
  } finally {stub.restore();}
});
