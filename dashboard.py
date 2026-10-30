"""
IFT 533 Phase III - Austin short-term rentals dashboard (Python Bokeh)

Input : austin_listings_tidy.csv (from preprocess.py)
Output: austin_str_dashboard.html - one self-contained file; every control works
        in the browser (CustomJS), so it can be published on any static host
        (e.g. GitHub Pages) with no login.

Run   : python dashboard.py
"""
import math
import numpy as np
import pandas as pd
from bokeh.io import output_file, save, curdoc
from bokeh.layouts import column, row
from bokeh.models import (ColumnDataSource, CustomJS, CheckboxGroup, RangeSlider,
                          MultiChoice, RadioButtonGroup, Select, Div, Span,
                          NumeralTickFormatter, HoverTool, LabelSet, Range1d)
from bokeh.plotting import figure
from bokeh.resources import INLINE

BLUE, ORANGE, GREY = "#2F6FD6", "#E07B12", "#9AA3AE"
H = 300            # every plot the same height (layout rubric)
W = 420

df = pd.read_csv("data/austin_listings_tidy.csv", dtype={"zip": str, "listing_id": str, "host_id": str})

# Web Mercator for the map tiles
k = 6378137.0
df["mx"] = df["longitude"] * (k * math.pi / 180.0)
df["my"] = np.log(np.tan((90 + df["latitude"]) * math.pi / 360.0)) * k
rng = np.random.default_rng(533)
df["bed_j"] = df["bedrooms"].clip(upper=8) + rng.uniform(-0.25, 0.25, len(df))

cols = ["room_type", "zip", "mx", "my", "price", "bedrooms", "bed_j", "host_id", "host_type",
        "superhost", "rating", "cleanliness", "location_score", "occupancy_rate", "revenue",
        "license_shown", "first_review_year"]
m = df[cols].copy()
for c in ["price", "bedrooms", "bed_j", "rating", "cleanliness", "location_score",
          "occupancy_rate", "revenue", "first_review_year"]:
    m[c] = m[c].astype(float)            # NaN travels to JS as NaN
m["superhost"] = m["superhost"].astype(str).str.lower().eq("true")
m["license_shown"] = m["license_shown"].astype(str).str.lower().eq("true")
master = ColumnDataSource(m)

ROOMS = ["Entire home/apt", "Private room", "Hotel room", "Shared room"]
ZIPS = sorted(df["zip"].dropna().unique().tolist())
YMIN, YMAX = int(df["first_review_year"].min()), int(df["first_review_year"].max())

def fig(title, **kw):
    p = figure(title=title, height=H, width=kw.pop("width", W), toolbar_location=None,
               tools="", **kw)
    p.outline_line_color = None
    p.title.text_font_size = "12pt"
    p.title.text_font_style = "normal"
    p.axis.axis_line_color = GREY
    p.axis.major_tick_line_color = GREY
    p.axis.minor_tick_line_color = None
    p.axis.major_label_text_color = "#444444"
    p.grid.grid_line_color = "#ECEEF1"
    return p

# ---------- sources each plot draws from (filled by the JS update) ----------
s1 = ColumnDataSource(dict(x=[], y=[], c=[]))
s2 = ColumnDataSource(dict(left=[], right=[], top=[]))
s3 = ColumnDataSource(dict(zip=[], med=[], n=[], lab=[]))
s4 = ColumnDataSource(dict(room=[], med=[], occ=[], lab=[]))
s5 = ColumnDataSource(dict(zip=[], pct=[], c=[], lab=[]))
s6 = ColumnDataSource(dict(ht=[], val=[], c=[], lab=[]))
s7 = ColumnDataSource(dict(g=[], q1=[], q2=[], q3=[], lo=[], hi=[]))
s8 = ColumnDataSource(dict(x=[], y=[]))
s9 = ColumnDataSource(dict(x=[], y=[]))
s9m = ColumnDataSource(dict(x=[], y=[]))
s10 = ColumnDataSource(dict(x=[], y=[]))
meta = ColumnDataSource(dict(city_med=[0], city_lic=[0], top10=[0], n=[0]))

# P1 map
p1 = fig("P1 · Where listings are (orange = entire home)", x_axis_type="mercator",
         y_axis_type="mercator", match_aspect=True)
import xyzservices.providers as xyz
p1.add_tile(xyz.Esri.WorldGrayCanvas)
p1.scatter("x", "y", source=s1, size=3, color="c", alpha=0.5, line_color=None)
p1.axis.visible = False
p1.grid.visible = False

# P3 median price by ZIP
p3 = fig("P3 · Median price, 15 busiest ZIPs (dashed = city)", y_range=[], x_range=Range1d(0, 1))
p3.hbar(y="zip", right="med", height=0.6, source=s3, color=BLUE)
city_line = Span(location=0, dimension="height", line_color=GREY, line_dash="dashed", line_width=1)
p3.add_layout(city_line)
p3.add_layout(LabelSet(x="med", y="zip", text="lab", source=s3, x_offset=4, y_offset=-6,
                       text_font_size="8pt", text_color="#444444"))
p3.xaxis.formatter = NumeralTickFormatter(format="$0")
p3.ygrid.grid_line_color = None
p3.add_tools(HoverTool(tooltips=[("ZIP", "@zip"), ("Median", "@med{$0}"), ("Listings", "@n")]))

# P5 % licensed by ZIP
p5 = fig("P5 · % with a license (orange = below city)", y_range=[],
         x_range=Range1d(0, 1))
p5.hbar(y="zip", right="pct", height=0.6, source=s5, color="c")
lic_line = Span(location=0, dimension="height", line_color=GREY, line_dash="dashed", line_width=1)
p5.add_layout(lic_line)
p5.add_layout(LabelSet(x="pct", y="zip", text="lab", source=s5, x_offset=4, y_offset=-6,
                       text_font_size="8pt", text_color="#444444"))
p5.xaxis.formatter = NumeralTickFormatter(format="0%")
p5.ygrid.grid_line_color = None

# P2 histogram
p2 = fig("P2 · How nightly prices are spread ($50 bins)")
p2.quad(left="left", right="right", top="top", bottom=0, source=s2, color=BLUE,
        line_color="white", line_width=1)
p2.xaxis.formatter = NumeralTickFormatter(format="$0")
p2.xgrid.grid_line_color = None
p2.yaxis.axis_label = "listings"
p2.add_tools(HoverTool(tooltips=[("Price", "@left{$0}–@right{$0}"), ("Listings", "@top")]))

# P4 room type
p4 = fig("P4 · Median price by room type · % booked", y_range=ROOMS[::-1], x_range=Range1d(0, 1))
p4.hbar(y="room", right="med", height=0.5, source=s4, color=BLUE)
p4.add_layout(LabelSet(x="med", y="room", text="lab", source=s4, x_offset=4, y_offset=-6,
                       text_font_size="9pt", text_color="#444444"))
p4.xaxis.formatter = NumeralTickFormatter(format="$0")
p4.ygrid.grid_line_color = None

# P9 scatter
p9 = fig("P9 · Price vs bedrooms (orange = median)")
p9.scatter("x", "y", source=s9, size=3, color=BLUE, alpha=0.12, line_color=None)
p9.line("x", "y", source=s9m, color=ORANGE, line_width=2)
p9.scatter("x", "y", source=s9m, size=5, color=ORANGE)
p9.xaxis.axis_label = "bedrooms (8 = 8+)"
p9.yaxis.formatter = NumeralTickFormatter(format="$0")
p9.xgrid.grid_line_color = None

# P6 host type
p6 = fig("P6 · Listings by host type", x_range=["1 single", "2 small (2-5)", "3 commercial (6+)"],
         width=360, y_range=Range1d(0, 1))
p6.vbar(x="ht", top="val", width=0.55, source=s6, color="c")
p6.add_layout(LabelSet(x="ht", y="val", text="lab", source=s6, y_offset=3, text_align="center",
                       text_font_size="9pt", text_color="#444444"))
p6.xgrid.grid_line_color = None
fmt6 = NumeralTickFormatter(format="0,0")
p6.yaxis.formatter = fmt6

# P7 box plot
p7 = fig("P7 · Rating: superhosts vs others", x_range=["Superhost", "Other host"], width=340)
p7.segment(x0="g", x1="g", y0="lo", y1="hi", source=s7, color=GREY, line_width=1)
p7.vbar(x="g", bottom="q1", top="q3", width=0.4, source=s7, color=BLUE, alpha=0.85)
p7.rect(x="g", y="q2", width=0.4, height=0.004, source=s7, color="white")
p7.yaxis.axis_label = "score (1–5); whiskers = 5th–95th pct"
p7.xgrid.grid_line_color = None

# P8 Pareto
p8 = fig("P8 · Share of revenue earned by the biggest hosts", x_range=Range1d(0, 1),
         y_range=Range1d(0, 1.02))
p8.line("x", "y", source=s8, color=BLUE, line_width=2)
p8.add_layout(Span(location=0.8, dimension="width", line_color=GREY, line_dash="dashed", line_width=1))
p8_note = Div(text="", styles={"font-size": "10pt", "color": "#444"})
p8.xaxis.axis_label = "share of hosts (largest first)"
p8.yaxis.axis_label = "share of revenue"
p8.xaxis.formatter = NumeralTickFormatter(format="0%")
p8.yaxis.formatter = NumeralTickFormatter(format="0%")

# P10 line
p10 = fig("P10 · Listings by year of first review", width=600, y_range=Range1d(0, 1))
p10.line("x", "y", source=s10, color=BLUE, line_width=2)
p10.scatter("x", "y", source=s10, size=4, color=BLUE)
p10.yaxis.axis_label = "listings"
p10.xgrid.grid_line_color = None
p10_note = Div(text="Only listings active in Sep 2026 are counted, so early years undercount "
                    "listings that have since closed.", width=260,
               styles={"font-size": "9pt", "color": "#666"})

# ---------- controls ----------
c1 = CheckboxGroup(labels=ROOMS, active=[0, 1, 2, 3], inline=True)
c3 = MultiChoice(options=ZIPS, value=[], placeholder="All ZIP codes", width=420)
c2 = RangeSlider(start=10, end=1000, value=(10, 1000), step=10, title="Nightly price ($)",
                 format="$0,0", width=420)
c4 = RadioButtonGroup(labels=["Listings", "Revenue"], active=0, orientation="vertical")
c5 = RangeSlider(start=YMIN, end=YMAX, value=(YMIN, YMAX), step=1, title="First-review year",
                 width=220, format="0")
c6 = Select(options=["Overall", "Cleanliness", "Location"], value="Overall", width=130)

JS = """
const d = master.data, n = d.room_type.length;
const rooms = new Set(c1.active.map(i => c1.labels[i]));
const zips = new Set(c3.value);
const [pmin, pmax] = c2.value;
const [ymin, ymax] = c5.value;
const med = a => { if (!a.length) return NaN; a.sort((x,y)=>x-y); const m=a.length>>1; return a.length%2 ? a[m] : (a[m-1]+a[m])/2; };
const q = (a, p) => { if (!a.length) return NaN; const i=(a.length-1)*p, lo=Math.floor(i), hi=Math.ceil(i); return a[lo]+(a[hi]-a[lo])*(i-lo); };
const ok = i => rooms.has(d.room_type[i]);
const okZip = i => zips.size === 0 || zips.has(d.zip[i]);
const hasP = i => !isNaN(d.price[i]);
const inP = i => hasP(i) && d.price[i] >= pmin && d.price[i] <= pmax;
const usd = v => '$' + Math.round(v).toLocaleString('en-US');

// P1 map  (C1 + C3)
const X=[],Y=[],C=[];
for (let i=0;i<n;i++) if (ok(i)&&okZip(i)) { X.push(d.mx[i]); Y.push(d.my[i]); C.push(d.room_type[i]==='Entire home/apt' ? '%(o)s' : '%(b)s'); }
s1.data = {x:X, y:Y, c:C};

// P3 + P5  (C1 + C3): 15 busiest ZIPs in the selection
const byZip = {}, allP = []; let licAll=0, cntAll=0;
for (let i=0;i<n;i++) { if (!ok(i)||!okZip(i)) continue;
  const z=d.zip[i]; (byZip[z] = byZip[z] || {p:[], n:0, lic:0});
  byZip[z].n++; if (d.license_shown[i]) byZip[z].lic++; if (hasP(i)) { byZip[z].p.push(d.price[i]); allP.push(d.price[i]); }
  cntAll++; if (d.license_shown[i]) licAll++; }
const top = Object.entries(byZip).sort((a,b)=>b[1].n-a[1].n).slice(0,15);
const r3 = top.map(([z,v]) => [z, med(v.p.slice()), v.n]).filter(r=>!isNaN(r[1])).sort((a,b)=>a[1]-b[1]);
s3.data = {zip:r3.map(r=>r[0]), med:r3.map(r=>r[1]), n:r3.map(r=>r[2]), lab:r3.map(r=>usd(r[1]))};
p3.y_range.factors = r3.map(r=>r[0]); p3.x_range.end = Math.max(1, ...r3.map(r=>r[1])) * 1.2;
const cityMed = med(allP.slice()); city_line.location = cityMed;
const cityLic = cntAll ? licAll/cntAll : 0; lic_line.location = cityLic;
const r5 = top.map(([z,v]) => [z, v.lic/v.n]).sort((a,b)=>a[1]-b[1]);
s5.data = {zip:r5.map(r=>r[0]), pct:r5.map(r=>r[1]), c:r5.map(r=>r[1]<cityLic?'%(o)s':'%(b)s'), lab:r5.map(r=>Math.round(r[1]*100)+'%%')};
p5.y_range.factors = r5.map(r=>r[0]);

// P2 histogram (C1 + C2)
const bw = 50, lo = Math.floor(pmin/bw)*bw, nb = Math.ceil((pmax-lo)/bw);
const cnt = new Array(nb).fill(0);
for (let i=0;i<n;i++) if (ok(i)&&inP(i)) { const b=Math.min(nb-1, Math.floor((d.price[i]-lo)/bw)); cnt[b]++; }
s2.data = {left:cnt.map((_,b)=>lo+b*bw), right:cnt.map((_,b)=>lo+(b+1)*bw), top:cnt};

// P4 room type (C1 + C2)
const rp = {}, ro = {};
for (let i=0;i<n;i++) if (ok(i)&&inP(i)) { const r=d.room_type[i]; (rp[r]=rp[r]||[]).push(d.price[i]); (ro[r]=ro[r]||[]).push(d.occupancy_rate[i]); }
const R = Object.keys(rp);
s4.data = {room:R, med:R.map(r=>med(rp[r])), occ:R.map(r=>med(ro[r])), lab:R.map(r=>usd(med(rp[r].slice()))+' · '+Math.round(med(ro[r].slice())*100)+'%%')};
p4.x_range.end = Math.max(1, ...R.map(r=>med(rp[r].slice()))) * 1.35;

// P9 scatter (C1 + C2)
const sx=[], sy=[], bb={};
for (let i=0;i<n;i++) if (ok(i)&&inP(i)&&!isNaN(d.bedrooms[i])) { sx.push(d.bed_j[i]); sy.push(d.price[i]); const b=Math.min(8,d.bedrooms[i]); (bb[b]=bb[b]||[]).push(d.price[i]); }
s9.data = {x:sx, y:sy};
const bk = Object.keys(bb).map(Number).sort((a,b)=>a-b).filter(b=>bb[b].length>=10);
s9m.data = {x:bk, y:bk.map(b=>med(bb[b]))};

// P6 host type (C1 + C4)
const ht = ['1 single','2 small (2-5)','3 commercial (6+)'], hv = {}; ht.forEach(h=>hv[h]=0);
for (let i=0;i<n;i++) if (ok(i)) hv[d.host_type[i]] += c4.active===0 ? 1 : (isNaN(d.revenue[i])?0:d.revenue[i]);
const tot = ht.reduce((s,h)=>s+hv[h],0);
s6.data = {ht:ht, val:ht.map(h=>hv[h]), c:ht.map(h=>h.startsWith('3')?'%(o)s':'%(b)s'), lab:ht.map(h=>tot?Math.round(hv[h]/tot*100)+'%%':'')};
p6.y_range.end = Math.max(1, ...ht.map(h=>hv[h])) * 1.15;
p6.title.text = c4.active===0 ? 'P6 · Listings by host type' : 'P6 · Estimated revenue by host type';
fmt6.format = c4.active===0 ? '0,0' : '$0.0a';

// P7 box plot (C1 + C6)
const key = {Overall:'rating', Cleanliness:'cleanliness', Location:'location_score'}[c6.value];
const g = {Superhost:[], 'Other host':[]};
for (let i=0;i<n;i++) if (ok(i)) { const v=d[key][i]; if (!isNaN(v)) g[d.superhost[i]?'Superhost':'Other host'].push(v); }
const G = Object.keys(g); G.forEach(k=>g[k].sort((a,b)=>a-b));
s7.data = {g:G, q1:G.map(k=>q(g[k],.25)), q2:G.map(k=>q(g[k],.5)), q3:G.map(k=>q(g[k],.75)), lo:G.map(k=>q(g[k],.05)), hi:G.map(k=>q(g[k],.95))};
p7.title.text = 'P7 · ' + c6.value + ' score: superhosts vs others';

// P8 Pareto (C1)
const hr = {};
for (let i=0;i<n;i++) if (ok(i) && !isNaN(d.revenue[i])) hr[d.host_id[i]] = (hr[d.host_id[i]]||0) + d.revenue[i];
const hvals = Object.values(hr).sort((a,b)=>b-a), H = hvals.length, T = hvals.reduce((s,v)=>s+v,0);
const px=[0], py=[0]; let run=0, top10=0;
hvals.forEach((v,i)=>{ run+=v; if (i < Math.ceil(H*0.1)) top10 = run; if (i%%5===0 || i===H-1) { px.push((i+1)/H); py.push(run/T); } });
s8.data = {x:px, y:py};
p8.title.text = 'P8 · Top 10%% of hosts earn ' + (T?Math.round(top10/T*100):0) + '%% of revenue';

// P10 line (C1 + C5)
const yc = {};
for (let i=0;i<n;i++) { const y=d.first_review_year[i]; if (ok(i) && !isNaN(y) && y>=ymin && y<=ymax) yc[y]=(yc[y]||0)+1; }
const yrs = Object.keys(yc).map(Number).sort((a,b)=>a-b);
s10.data = {x:yrs, y:yrs.map(y=>yc[y])}; p10.y_range.end = Math.max(1, ...yrs.map(y=>yc[y])) * 1.1;

let shown=0; for (let i=0;i<n;i++) if (ok(i)) shown++;
header.text = '<b>' + shown.toLocaleString('en-US') + '</b> of ' + n.toLocaleString('en-US') + ' listings shown · city median price ' + usd(cityMed) + ' · ' + Math.round(cityLic*100) + '%% show a license';
""".replace("%%", "%").replace("%(o)s", ORANGE).replace("%(b)s", BLUE)

header = Div(text="", styles={"font-size": "11pt", "color": "#333"})
args = dict(master=master, c1=c1, c2=c2, c3=c3, c4=c4, c5=c5, c6=c6, s1=s1, s2=s2, s3=s3, s4=s4,
            s5=s5, s6=s6, s7=s7, s8=s8, s9=s9, s9m=s9m, s10=s10, p3=p3, p5=p5, p6=p6, p7=p7,
            p8=p8, p4=p4, p10=p10, fmt6=fmt6, city_line=city_line, lic_line=lic_line, header=header)
update = CustomJS(args=args, code=JS)
c1.js_on_change("active", update)
c2.js_on_change("value", update)
c3.js_on_change("value", update)
c4.js_on_change("active", update)
c5.js_on_change("value", update)
c6.js_on_change("value", update)

def label(t):
    return Div(text=f"<span style='font-size:10pt;color:#555'>{t}</span>")

title = Div(text="<h2 style='margin:0'>Austin short-term rentals, September 2026</h2>"
                 "<span style='color:#555'>Inside Airbnb, Austin TX listings scraped Sep 17, 2026 · "
                 "built for city compliance staff and prospective hosts</span>", width=1300)
top_controls = row(label("C1 · Room type (all plots)"), c1)
row1 = column(row(label("C3 · ZIP code (P1, P3, P5)"), c3), row(p1, p3, p5))
row2 = column(row(c2, label("C2 drives P2, P4, P9")), row(p2, p4, p9))
row3 = row(column(label("C4 · Measure"), c4), p6,
           p7, column(label("C6 · Score"), c6), p8)
row4 = row(p10, column(label("C5 · Years (P10 only)"), c5, p10_note))

layout = column(title, top_controls, header, row1, row2, row3, row4)
doc = curdoc()
doc.add_root(layout)
doc.js_on_event("document_ready", update)
doc.title = "Austin short-term rentals · IFT 533"

output_file("austin_str_dashboard.html", title="Austin short-term rentals · IFT 533")
save(doc, resources=INLINE)
print("wrote austin_str_dashboard.html")
