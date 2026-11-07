# What is translated

Policy used on the sample (and by the code):

| Category | Action | Examples |
|----------|--------|----------|
| Header labels | Translate | Style Name, Fit Block Reference, Season/Release |
| BOM / description text | Translate | Placement, Main Fabric, Piping Cord, topstitch notes |
| Color names (when descriptive) | Translate | Blue Light, Mocha Mousse, Ultimate Gray |
| Design pack artwork (top-right graphic) | Do not touch | RAMESES II, Kings of Egypt II, VIEW OF HEAD, any text inside the artwork |
| Placement placeholders labelled “Design pack image” | Translate the label only; do not alter nearby drawings | The two small boxes on the pants sketch |
| Codes | Preserve | YKK: 316, YKK: 366, #5 |
| Measurements and quantities | Preserve | 5.5 oz, 60", 1/8", 18" L, pure numbers |
| Empty header values | Leave empty | Style Name value is blank → no translation needed |
| Already Chinese | Skip | — |
| Low-confidence / handwriting | Flag, do not auto-translate | — |

The design-pack region is excluded before translation.  
Anything whose center falls inside that region is never modified.  
Codes and measurements are additionally filtered by a preserve pattern so they are not sent to the translator even if they lie outside the artwork.
