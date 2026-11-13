# Mural build prompts — IFT 533 project board

Paste these one at a time into the Claude panel in Chrome, on the tab showing
the mural. Wait for each to finish before sending the next.

Board: https://app.mural.co/t/aznights2554/m/aznights2554/1793393514861/af35872766bd40d5d7c7cbeeb304be85813bb933

Blueprint (what this builds): https://claude.ai/artifact/PzNmGD581cyum7iq2tioQy

---

## Paste 1 — Setup and Zone 1

```
Rename this mural to "IFT 533 — Project Board".

Build Zone 1 in the top-left of the canvas. Use real Mural sticky notes
and text elements. Leave plenty of empty canvas to the right and below —
eleven more zones are coming.

Title text element: "Z1 · TEAM CHARTER & LEGEND"

Four sticky notes in a row, each a different colour:
  Blue    "Data lead — [name] — [ASU email]"
  Green   "Viz lead — [name] — [ASU email]"
  Yellow  "Report lead — [name] — [ASU email]"
  Purple  "Integrator — [name] — [ASU email]"

Two stickies in a row below those:
  Red     "BLOCKED — needs a decision"
  Grey    "DECIDED — locked, do not edit"

Text element below: "Each member writes only in their own colour.
Phase II Section 6 scores each student on their own contribution."

Four stickies in a column at the far left edge, as a deadline strip:
  "Nov 19 — Team + Mural link (2 pts)"
  "Nov 22 — Phase I Planning (70 pts)"
  "Nov 29 — Phase II Decisions (70 pts)"
  "Dec 4 — Phase III Dashboard (70 pts)"
```

---

## Paste 2 — Phase I zones

```
Same mural. Build five zones in a row to the right of Zone 1, left to
right, well spaced. Each zone gets a title text element above its contents.

ZONE 2 — title "Z2 · DATASET SCOUTING"
Six stickies, same colour, one per repository:
  "Kaggle"
  "UCI ML Repository"
  "data.gov"
  "Inside Airbnb"
  "WHO / World Bank"
  "BTS TranStats (flight delays)"
Text below: "Per dataset: rows x cols, column data types, what other
analysts used it for, what could be visualised."

ZONE 3 — title "Z3 · DATASET DECISION"
Draw a large empty square outline as a 2x2 matrix.
Text label on the horizontal axis: "Attribute type coverage →"
Text label on the vertical axis: "User story strength ↑"
Five stickies placed loosely on it:
  "Olympic athletes 120 yrs — medal is a real ordinal"
  "Inside Airbnb listings — review score bands"
  "FAA wildlife strikes — damage level ordinal"
  "Flight delays BTS — delay severity bands"
  "311 service requests — priority level"
Text below: "Three dots each. Winner copies into Z4. Runner-up stays as
the fallback."

ZONE 4 — title "Z4 · ATTRIBUTE ERD"
Draw three rectangles side by side as entity boxes, each with a darker
header strip across the top.
Header text: box 1 "FACT TABLE", box 2 "DIMENSION", box 3 "DERIVED".
Inside each box, a text line: "column | Cat / Ord / Int / Ratio | domain"
Draw an arrow from box 2 to box 1, and a dashed arrow from box 3 to box 1.
Four stickies beside the boxes:
  "PK badge on identifiers"
  "FK + connector wherever two files join"
  "Count nulls per column now — it decides preprocessing"
  "Type columns from the data, not from the description"

ZONE 5 — title "Z5 · PROSPECTIVE USERS"
Draw two large rectangles as persona cards.
In each, four text labels as quadrants: "Says" "Thinks" "Does" "Pains"
Three stickies beside them:
  "Persona: role + the decision they make"
  "How often do they look at this?"
  "What does a wrong answer cost them?"

ZONE 6 — title "Z6 · QUESTION STORM"
Six stickies in a row as cluster headers, all one colour:
  "DISTRIBUTION"
  "COMPARISON"
  "TREND OVER TIME"
  "RATIO / PROPORTION"
  "OUTLIERS"
  "CORRELATION"
Text below: "Eight minutes silent, everyone in their own colour, no
talking. Target 30+ questions. Assignment floor is 10. Worth 30 pts."
```

---

## Paste 3 — Phase II zones

```
Same mural. Build five more zones in a row BELOW the Phase I row, left to
right, well spaced. Title text element above each.

ZONE 7 — title "Z7 · TOOL DECISION"
Draw a large rectangle split down the middle into two columns (a T-chart).
Column headers as text: "TABLEAU PUBLIC" and "PYTHON BOKEH"
Stickies in the Tableau column:
  "Required publishing target"
  "Public link, no login needed"
Stickies in the Bokeh column:
  "Already built a dashboard in Lab 6"
  "Full control in Python"
Two stickies below the chart:
  "DECISION: ___ because ___"
  "EXTRA CREDIT (5 pts): Prep Builder / Table Calculations / Story — pick one"

ZONE 8 — title "Z8 · PREPROCESSING FLOW"
Draw five rectangles left to right connected by arrows, each labelled:
  "raw file"
  "missing values"
  "type casts"
  "derived columns"
  "tidy extract"
Two stickies below:
  "One node per transformation — name the column it creates"
  "Note row count before and after"

ZONE 9 — title "Z9 · THE FINAL TEN"
Ten stickies in two columns of five, all the same colour, numbered:
  "Q1." "Q2." "Q3." "Q4." "Q5." "Q6." "Q7." "Q8." "Q9." "Q10."
Text below: "Five dots each on the Z6 clusters. Top scorers land here.
Ten minimum. Phrase each the way a user would say it aloud. Worth 30 pts."

ZONE 10 — title "Z10 · PLOT DRAFTS"
Draw ten empty squares in two rows of five, all the same size, aligned.
Label them with text: "P1" through "P10".
Four stickies beside the grid:
  "Each frame: sketch + question number + chart type"
  "Pre-attentive attributes used — list the FEWEST that work"
  "Position / length / hue / size / shape / orientation"
  "One shared colour palette across all ten. Worth 20 pts + 20 rubric pts"

ZONE 11 — title "Z11 · LAYOUT & CONTROLS"
Draw one large rectangle as the dashboard canvas, divided into a grid of
six smaller rectangles.
Four stickies beside it:
  "Control driving several plots → sits ABOVE that group"
  "Control driving one plot → sits BESIDE that plot"
  "Wide numeric range → slider, never a dropdown"
  "Per control: what it filters, which plots, value range, source column"
```

---

## Paste 4 — Phase III zone and sharing

```
Same mural. Build one final zone as a wide band across the BOTTOM of the
whole board, below everything else.

Title text element: "Z12 · BUILD / PREFLIGHT / LINKS"

Draw four horizontal swimlanes as long rectangles stacked vertically.
Label them with text at the left of each:
  "Data lead"
  "Viz lead"
  "Report lead"
  "Integrator"
Across the top of the swimlanes, four column header texts:
  "TO DO"   "BUILDING"   "REVIEW"   "DONE"

To the right of the swimlanes, four stickies as a rubric preflight:
  "Documentation — all sections present (15 pts)"
  "Data-ink maximised — no redundancy (20 pts)"
  "Pre-attentive economy — fewest attributes (20 pts)"
  "Layout — aligned, controls near their plots (15 pts)"

Three stickies below those, a different colour:
  "DATASET URL: ___"
  "MURAL URL (view-only): ___"
  "TABLEAU PUBLIC URL: ___"

Finally: open the Share menu and set this mural so anyone with the link
can VIEW it without logging in. Then tell me the view-only link.
```

---

## After it finishes

1. Check the view-only link in a private window — it must open with no login.
2. Paste that link into the Canvas text box for Team Formation (due Nov 19).
3. Fill the `[name]` placeholders in Zone 1 and assign colours for real.
4. The dataset decision in Zone 3 is the team's to make in class.
