import test from 'node:test';
import assert from 'node:assert/strict';
import {filterTripDates} from '../app/domain.mjs';
test('date filters are inclusive and do not change the saved trip array',()=>{
 const trips=[{id:'a',trip_date:'2026-01-01'},{id:'b',trip_date:'2026-10-20'},{id:'c',trip_date:null}];
 assert.deepEqual(filterTripDates(trips,{from:'2026-10-20',to:'2026-10-20',includeUndated:false}).map(t=>t.id),['b']);
 assert.equal(filterTripDates(trips,{from:'2026-10-20'}).length,2);assert.equal(trips.length,3);
});
test('invalid or reversed date ranges are rejected',()=>{
 assert.throws(()=>filterTripDates([],{from:'2026-02-30'}));assert.throws(()=>filterTripDates([],{from:'2026-10-21',to:'2026-10-20'}));
});
