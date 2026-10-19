import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
const $=id=>document.getElementById(id),params=new URLSearchParams(location.search),data=await fetch(params.get('programme')||'./programme.json').then(x=>x.json());
const scene=new THREE.Scene();scene.background=new THREE.Color(0x233340);scene.fog=new THREE.Fog(0x233340,200,450);
const camera=new THREE.PerspectiveCamera(48,innerWidth/innerHeight,.12,650);camera.position.set(100,80,115);
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,1.25));renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;renderer.localClippingEnabled=true;$('scene').appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,5,0);controls.minDistance=.7;controls.maxDistance=220;controls.maxPolarAngle=Math.PI*.495;controls.enableDamping=false;
scene.add(new THREE.HemisphereLight(0xe9f3ff,0x776558,2.1));const sun=new THREE.DirectionalLight(0xffe0b3,3.2);sun.position.set(-50,80,40);scene.add(sun);const fill=new THREE.DirectionalLight(0xaac9ff,1);fill.position.set(50,30,-50);scene.add(fill);
let model,cut=false,selection='ALL',floor='ALL',frameRequested=false;const plane=new THREE.Plane(new THREE.Vector3(0,-1,0),1.6);
window.previewDiagnostics={frames:0,modelLoaded:false,renderCallCompleted:false};
function fitViewport(){const left=innerWidth>700?344:0;renderer.setViewport(left,0,innerWidth-left,innerHeight);renderer.setScissor(left,0,innerWidth-left,innerHeight);renderer.setScissorTest(true);camera.aspect=(innerWidth-left)/innerHeight;camera.updateProjectionMatrix();}
fitViewport();
function draw(){if(!frameRequested){frameRequested=true;requestAnimationFrame(()=>{frameRequested=false;renderer.render(scene,camera);window.previewDiagnostics={frames:window.previewDiagnostics.frames+1,modelLoaded:!!model,renderCallCompleted:!!model,selection,floor,calls:renderer.info.render.calls,triangles:renderer.info.render.triangles,geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures};if(model)$('loading').style.display='none';});}}
controls.addEventListener('change',draw);addEventListener('resize',()=>{renderer.setSize(innerWidth,innerHeight);fitViewport();draw();});
const xyz=p=>new THREE.Vector3(p[0],p[2],-p[1]);
function view(pos,target){camera.position.copy(pos);controls.target.copy(target);controls.update();draw();}
function building(){return data.buildings.find(b=>b.id===selection);}
function selectedFloor(){return building()?.floors.find(f=>f.id===floor);}
function metadata(o){let n=o;while(n&&!n.userData.building_id)n=n.parent;return n?.userData||{};}
function update(){if(!model)return;const b=building(),f=selectedFloor();plane.constant=f?f.datum_m+1.6:1.65;
 model.traverse(o=>{if(!o.isMesh)return;const d=metadata(o);let visible=selection==='ALL'||d.building_id===selection;if(f)visible=visible&&d.floor_id===floor;if(cut&&['wall_high','ceiling','roof','exterior','lighting'].includes(d.layer))visible=false;o.visible=visible;});
 renderer.clippingPlanes=[];$('cutaway').textContent=cut?'Restore uncut geometry':'Show cutaway / hide upper walls';
 $('title').textContent=b?`${b.brand}${f?' · '+f.id:''}`:'The Christmas square';$('programme').textContent=f?f.programme:b?b.business:'Orbit, pan and zoom to explore the actual textured portable model.';
 if(b){const [x,y]=b.centre_xy_m;const h=f?f.datum_m:2;view(xyz([x-16,y-19,h+19]),xyz([x,y,h+.5]));}else draw();}
for(const b of data.buildings){const option=document.createElement('option');option.value=b.id;option.textContent=`${b.id} · ${b.brand}`;$('building').appendChild(option);}
$('building').onchange=()=>{selection=$('building').value;floor='ALL';cut=false;$('floor').innerHTML='<option value="ALL">All floors · intact exterior</option>';for(const f of building()?.floors||[]){const o=document.createElement('option');o.value=f.id;o.textContent=f.id;$('floor').appendChild(o);}update();};
$('floor').onchange=()=>{floor=$('floor').value;cut=floor!=='ALL';update();};$('cutaway').onclick=()=>{cut=!cut;update();};
$('reset').onclick=()=>{selection='ALL';floor='ALL';cut=false;$('building').value='ALL';$('floor').innerHTML='<option value="ALL">All floors · intact exterior</option>';update();view(new THREE.Vector3(100,80,115),new THREE.Vector3(0,5,0));};
$('hero').onclick=()=>{$('reset').onclick();view(xyz([13,-12,2.4]),xyz([-7,23,4.8]));};
$('download').href=data.release_url;
new GLTFLoader().load(params.get('model')||'./model.glb',g=>{window.previewDiagnostics.modelUrl=params.get('model')||'./model.glb';model=g.scene;model.traverse(o=>{if(o.isLight){o.visible=false;return;}if(!o.isMesh)return;o.frustumCulled=true;for(const m of Array.isArray(o.material)?o.material:[o.material]){if(m.transmission>0){m.transmission=0;m.transparent=true;m.opacity=.27;m.depthWrite=false;}m.needsUpdate=true;}});scene.add(model);$('loadtext').textContent='Geometry loaded · preparing the first actual WebGL frame';controls.update();draw();},e=>{if(e.total){$('progress').value=e.loaded/e.total;$('loadtext').textContent=`${Math.round(e.loaded/1048576)} / ${Math.round(e.total/1048576)} MB · loading real textured geometry`;}},e=>{$('error').textContent='The model could not load. Download the verified packed native using the link in the sidebar.\n'+e.message;console.error(e);});
