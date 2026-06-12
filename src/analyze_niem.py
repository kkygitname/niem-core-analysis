from pathlib import Path
from lxml import etree
from collections import Counter, defaultdict
import json, csv, re, math

xsd_path = Path('niem-core.xsd')
out = Path('.')
(out/'data').mkdir(parents=True, exist_ok=True)
(out/'docs').mkdir(parents=True, exist_ok=True)
(out/'visualizations').mkdir(parents=True, exist_ok=True)
(out/'src').mkdir(parents=True, exist_ok=True)

NS={'xs':'http://www.w3.org/2001/XMLSchema'}
tree=etree.parse(str(xsd_path))
root=tree.getroot()

def local(q):
    if q is None: return None
    return q.split(':')[-1]

def doc(node):
    d=node.find('xs:annotation/xs:documentation', NS)
    return ' '.join(''.join(d.itertext()).split()) if d is not None else ''

def ext_base(ct):
    ext=ct.find('.//xs:extension', NS)
    return ext.get('base') if ext is not None else None

def simple_base(st):
    r=st.find('.//xs:restriction', NS)
    if r is not None: return r.get('base')
    l=st.find('.//xs:list', NS)
    if l is not None: return l.get('itemType')
    return None

complex_types=[]; simple_types=[]; elements=[]; imports=[]; local_terms=[]
for im in root.findall('xs:import', NS):
    imports.append({'namespace': im.get('namespace'), 'schemaLocation': im.get('schemaLocation')})
for lt in root.findall('.//{https://docs.oasis-open.org/niemopen/ns/model/appinfo/6.0/}LocalTerm'):
    local_terms.append({'term':lt.get('term'), 'literal':lt.get('literal'), 'definition':lt.get('definition')})
for ct in root.findall('xs:complexType', NS):
    name=ct.get('name')
    children=[local(e.get('ref')) for e in ct.findall('.//xs:sequence/xs:element', NS) if e.get('ref')]
    base=ext_base(ct)
    kind='complex'
    if ct.find('xs:simpleContent', NS) is not None: kind='simpleContent-wrapper'
    elif ct.find('xs:complexContent', NS) is not None: kind='complexContent-extension'
    complex_types.append({'name':name,'base':base,'baseLocal':local(base),'childCount':len(children),'children':children,'documentation':doc(ct),'kind':kind})
for st in root.findall('xs:simpleType', NS):
    enums=[e.get('value') for e in st.findall('.//xs:enumeration', NS)]
    simple_types.append({'name':st.get('name'),'base':simple_base(st),'baseLocal':local(simple_base(st)),'enumerationCount':len(enums),'enumerations':enums,'documentation':doc(st)})
for el in root.findall('xs:element', NS):
    elements.append({'name':el.get('name'),'type':el.get('type'),'typeLocal':local(el.get('type')),'ref':el.get('ref'),'substitutionGroup':el.get('substitutionGroup'),'substitutionGroupLocal':local(el.get('substitutionGroup')),'abstract':el.get('abstract')=='true','nillable':el.get('nillable')=='true','documentation':doc(el)})

# Edges
edges=[]
for ct in complex_types:
    if ct['baseLocal']:
        edges.append({'source':ct['name'],'target':ct['baseLocal'],'relation':'extends'})
    for ch in ct['children']:
        edges.append({'source':ct['name'],'target':ch,'relation':'hasElement'})
for el in elements:
    if el['typeLocal']:
        edges.append({'source':el['name'],'target':el['typeLocal'],'relation':'typedBy'})
    if el['substitutionGroupLocal']:
        edges.append({'source':el['name'],'target':el['substitutionGroupLocal'],'relation':'substitutionGroup'})
for st in simple_types:
    if st['baseLocal']:
        edges.append({'source':st['name'],'target':st['baseLocal'],'relation':'restrictsOrLists'})

# Summary
summary={
 'file':'niem-core.xsd',
 'targetNamespace':root.get('targetNamespace'),
 'version':root.get('version'),
 'schemaDocumentation': doc(root),
 'imports':len(imports),
 'localTerms':len(local_terms),
 'complexTypes':len(complex_types),
 'simpleTypes':len(simple_types),
 'elements':len(elements),
 'abstractElements':sum(1 for e in elements if e['abstract']),
 'nillableElements':sum(1 for e in elements if e['nillable']),
 'substitutionGroupElements':sum(1 for e in elements if e['substitutionGroup']),
 'totalEdges':len(edges),
 'relationCounts':Counter(e['relation'] for e in edges),
}

# top lists
summary['topComplexTypesByChildCount']=sorted([{k:v for k,v in c.items() if k!='children'} for c in complex_types], key=lambda x:x['childCount'], reverse=True)[:20]
summary['topSimpleTypesByEnumerationCount']=sorted([{k:v for k,v in s.items() if k!='enumerations'} for s in simple_types], key=lambda x:x['enumerationCount'], reverse=True)[:20]
summary['topTypePrefixes']=Counter((e['type'] or '').split(':')[0] if e['type'] else '(none)' for e in elements)

# save data
for name, rows in [('complex_types',complex_types),('simple_types',simple_types),('elements',elements),('imports',imports),('local_terms',local_terms),('edges',edges)]:
    with open(out/'data'/f'{name}.json','w',encoding='utf-8') as f: json.dump(rows,f,indent=2,ensure_ascii=False)
    with open(out/'data'/f'{name}.csv','w',encoding='utf-8',newline='') as f:
        if rows:
            keys=list(rows[0].keys())
            w=csv.DictWriter(f,fieldnames=keys); w.writeheader()
            for r in rows:
                r2=dict(r)
                for k,v in r2.items():
                    if isinstance(v,(list,dict,Counter)): r2[k]=json.dumps(v,ensure_ascii=False)
                w.writerow(r2)
with open(out/'data'/'summary.json','w',encoding='utf-8') as f: json.dump(summary,f,indent=2,ensure_ascii=False,default=dict)

# Create selected focus subgraph top domains/types
focus_names=['ActivityType','PersonType','OrganizationType','LocationType','AddressType','ItemType','ConveyanceType','VehicleType','DocumentType','AssociationType','ContactInformationType','IdentificationType','MeasureType','DateType','CaseType','FacilityType']
# include neighborhood edges for focus
def add_neighborhood(names):
    s=set(names)
    for e in edges:
        if e['source'] in names or e['target'] in names:
            s.add(e['source']); s.add(e['target'])
    return s
focus_set=add_neighborhood(focus_names)
focus_edges=[e for e in edges if e['source'] in focus_set and e['target'] in focus_set]
with open(out/'data'/'focus_edges.json','w',encoding='utf-8') as f: json.dump(focus_edges,f,indent=2,ensure_ascii=False)

# Markdown report
md=[]
md.append('# NIEM Core 6.0 XSD Analysis\n')
md.append('This repository analyzes `niem-core.xsd`, the NIEM Core schema. The goal is to make the schema easier to inspect through summary tables, graph edges, and visualizations.\n')
md.append('## Schema metadata\n')
md.append(f'- Target namespace: `{summary["targetNamespace"]}`\n')
md.append(f'- Version: `{summary["version"]}`\n')
md.append(f'- Imports: **{summary["imports"]}**\n')
md.append(f'- Local terms: **{summary["localTerms"]}**\n')
md.append('\n## Parsed component counts\n')
for k in ['complexTypes','simpleTypes','elements','abstractElements','nillableElements','substitutionGroupElements','totalEdges']:
    md.append(f'- {k}: **{summary[k]}**\n')
md.append('\n## Relation counts\n')
for k,v in summary['relationCounts'].items(): md.append(f'- {k}: **{v}**\n')
md.append('\n## Top complex types by number of child elements\n')
md.append('| Rank | Complex type | Base type | Child elements | Description |\n|---:|---|---|---:|---|\n')
for i,r in enumerate(summary['topComplexTypesByChildCount'][:15],1):
    md.append(f"| {i} | `{r['name']}` | `{r['baseLocal'] or ''}` | {r['childCount']} | {r['documentation'][:140]} |\n")
md.append('\n## Top code/simple types by enumeration count\n')
md.append('| Rank | Simple type | Base | Enumerations | Description |\n|---:|---|---|---:|---|\n')
for i,r in enumerate(summary['topSimpleTypesByEnumerationCount'][:15],1):
    md.append(f"| {i} | `{r['name']}` | `{r['baseLocal'] or ''}` | {r['enumerationCount']} | {r['documentation'][:140]} |\n")
md.append('\n## Repository contents\n')
md.append('- `data/`: parsed CSV/JSON tables.\n- `visualizations/`: PNG/SVG/HTML visualizations.\n- `src/analyze_niem.py`: parser and visualization script.\n- `docs/analysis.md`: this analysis report.\n')
md.append('\n## How to reproduce\n')
md.append('```bash\npip install -r requirements.txt\npython src/analyze_niem.py\n```\n')
(out/'docs'/'analysis.md').write_text(''.join(md),encoding='utf-8')

# Requirements and src copy
(out/'requirements.txt').write_text('lxml\nnetworkx\nmatplotlib\n',encoding='utf-8')
# self-contained script with relative paths
script = Path(__file__).read_text(encoding='utf-8').replace("xsd_path = Path('niem-core.xsd')","xsd_path = Path('niem-core.xsd')").replace("out = Path('.')","out = Path('.')")
(out/'src'/'analyze_niem.py').write_text(script,encoding='utf-8')
# copy input
import shutil
shutil.copy2(xsd_path,out/'niem-core.xsd')

# Visualizations
import networkx as nx
import matplotlib.pyplot as plt
G=nx.DiGraph()
for e in edges:
    G.add_edge(e['source'], e['target'], relation=e['relation'])
# component counts bar
plt.figure(figsize=(9,5))
labels=['complexTypes','simpleTypes','elements','abstractElements','substitutionGroupElements']
vals=[summary[l] for l in labels]
plt.bar(labels, vals)
plt.xticks(rotation=25, ha='right')
plt.ylabel('Count')
plt.title('NIEM Core XSD component counts')
plt.tight_layout()
plt.savefig(out/'visualizations'/'component_counts.png',dpi=180)
plt.savefig(out/'visualizations'/'component_counts.svg')
plt.close()
# relation counts
plt.figure(figsize=(7,4))
rlabels=list(summary['relationCounts'].keys()); rvals=[summary['relationCounts'][r] for r in rlabels]
plt.bar(rlabels, rvals)
plt.ylabel('Edges')
plt.title('Parsed graph relation counts')
plt.tight_layout()
plt.savefig(out/'visualizations'/'relation_counts.png',dpi=180)
plt.savefig(out/'visualizations'/'relation_counts.svg')
plt.close()
# top complex horizontal
top=summary['topComplexTypesByChildCount'][:15]
plt.figure(figsize=(9,7))
plt.barh([r['name'] for r in reversed(top)], [r['childCount'] for r in reversed(top)])
plt.xlabel('Child element count')
plt.title('Top complex types by child element count')
plt.tight_layout()
plt.savefig(out/'visualizations'/'top_complex_types.png',dpi=180)
plt.savefig(out/'visualizations'/'top_complex_types.svg')
plt.close()
# Focus graph png
FG=nx.DiGraph()
for e in focus_edges:
    if e['relation'] in ('extends','hasElement'):
        FG.add_edge(e['source'],e['target'],relation=e['relation'])
# limit to manageable: focus + high-degree among focus
if FG.number_of_nodes()>80:
    deg=sorted(FG.degree, key=lambda x:x[1], reverse=True)
    keep=set(focus_names) | {n for n,d in deg[:80]}
    FG=FG.subgraph(keep).copy()
plt.figure(figsize=(18,14))
pos=nx.spring_layout(FG, seed=42, k=1.4, iterations=80)
nx.draw_networkx_nodes(FG,pos,node_size=[120+25*FG.degree(n) for n in FG.nodes()], alpha=.85)
nx.draw_networkx_edges(FG,pos,arrows=True,alpha=.35,arrowsize=10,width=.8)
nx.draw_networkx_labels(FG,pos,font_size=7)
plt.title('NIEM Core focus graph: major types and neighboring elements')
plt.axis('off')
plt.tight_layout()
plt.savefig(out/'visualizations'/'focus_graph.png',dpi=180)
plt.savefig(out/'visualizations'/'focus_graph.svg')
plt.close()
# graphml
nx.write_graphml(G, out/'data'/'niem_core_graph.graphml')
# Interactive HTML using vis-network CDN
nodes=set()
for e in focus_edges:
    nodes.add(e['source']); nodes.add(e['target'])
if len(nodes)>180:
    deg=Counter()
    for e in focus_edges:
        deg[e['source']]+=1; deg[e['target']]+=1
    nodes=set(focus_names)|{n for n,_ in deg.most_common(180)}
fedges=[e for e in focus_edges if e['source'] in nodes and e['target'] in nodes]
node_objs=[{'id':n,'label':n} for n in sorted(nodes)]
edge_objs=[{'from':e['source'],'to':e['target'],'label':e['relation'],'arrows':'to'} for e in fedges]
html=f'''<!doctype html><html><head><meta charset="utf-8"><title>NIEM Core Focus Graph</title><script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script><style>body{{font-family:Arial;margin:0}}#mynetwork{{width:100vw;height:94vh;border:1px solid #ddd}}.note{{padding:10px}}</style></head><body><div class="note"><b>NIEM Core focus graph</b>: major types and nearby schema components. Drag, zoom, and search in browser.</div><div id="mynetwork"></div><script>const nodes=new vis.DataSet({json.dumps(node_objs)}); const edges=new vis.DataSet({json.dumps(edge_objs)}); const container=document.getElementById('mynetwork'); const data={{nodes:nodes,edges:edges}}; const options={{nodes:{{shape:'dot',size:12,font:{{size:14}}}},edges:{{font:{{size:9,align:'middle'}},color:{{opacity:0.45}},smooth:true}},physics:{{stabilization:true,barnesHut:{{gravitationalConstant:-18000,springLength:160}}}},interaction:{{hover:true,navigationButtons:true,keyboard:true}}}}; new vis.Network(container,data,options);</script></body></html>'''
(out/'visualizations'/'focus_graph_interactive.html').write_text(html,encoding='utf-8')

# README
readme=f'''# NIEM Core XSD Analysis and Visualization

This repository contains an analysis of `niem-core.xsd` from NIEM Core 6.0.

## Key findings

- Target namespace: `{summary['targetNamespace']}`
- Schema version: `{summary['version']}`
- Complex types: **{summary['complexTypes']}**
- Simple types: **{summary['simpleTypes']}**
- Global elements: **{summary['elements']}**
- Abstract elements: **{summary['abstractElements']}**
- Substitution group elements: **{summary['substitutionGroupElements']}**
- Parsed graph edges: **{summary['totalEdges']}**

## Visualizations

![Component counts](visualizations/component_counts.png)

![Relation counts](visualizations/relation_counts.png)

![Top complex types](visualizations/top_complex_types.png)

![Focus graph](visualizations/focus_graph.png)

Open `visualizations/focus_graph_interactive.html` locally for an interactive network view.

## Data files

- `data/summary.json`: overall schema statistics
- `data/complex_types.csv`: complex type definitions, base types, and child counts
- `data/simple_types.csv`: simple type definitions and enumerations
- `data/elements.csv`: global element definitions
- `data/edges.csv`: schema graph edges
- `data/niem_core_graph.graphml`: full graph for Gephi/Cytoscape

## Reproduce

```bash
pip install -r requirements.txt
python src/analyze_niem.py
```

## Suggested GitHub upload

```bash
git init
git add .
git commit -m "Analyze and visualize NIEM Core XSD"
git branch -M main
git remote add origin https://github.com/<YOUR_ID>/niem-core-analysis.git
git push -u origin main
```

## License note

Check the license/terms of the original NIEM/OASIS schema before redistributing the source XSD publicly. If needed, keep only derived analysis files and link to the official schema source.
'''
(out/'README.md').write_text(readme,encoding='utf-8')

print(json.dumps(summary,indent=2,ensure_ascii=False,default=dict))
