// Customer deck. From this directory: npm install pptxgenjs@3.12.0 && node build.js
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pres.layout = "WIDE";
pres.author = "Jatinder Singh";
pres.title = "Paperlane lakehouse POC";
pres.subject = "Synthetic customer demonstration. Deployment NO-GO.";

const navy = "101820";
const teal = "0F6E6E";
const ink = "102033";
const muted = "5C6B7A";
const bg = "F4F7FB";
const card = "FFFFFF";
const stroke = "E1E8EF";
const warn = "9A6700";
const deny = "9B2C2C";
const ok = "1F7A4D";

function cardShadow() {
  return { type: "outer", color: "D9E3EC", blur: 8, offset: 2, angle: 135, opacity: 0.7 };
}

function header(slide, kicker, title) {
  slide.background = { color: bg };
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 13.333, h: 1.22, fill: { color: navy },
  });
  slide.addText(kicker, {
    x: 0.5, y: 0.18, w: 12.3, h: 0.28,
    fontFace: "Calibri", fontSize: 13, color: "C5D0DA", margin: 0,
  });
  slide.addText(title, {
    x: 0.5, y: 0.48, w: 12.3, h: 0.55,
    fontFace: "Georgia", fontSize: 28, color: "FFFFFF", margin: 0,
  });
}

function footer(slide, label) {
  slide.addText(label, {
    x: 0.5, y: 7.12, w: 12.3, h: 0.24,
    fontFace: "Calibri", fontSize: 11, color: muted, margin: 0,
  });
}

function panel(slide, x, y, w, h) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: card },
    line: { color: stroke, width: 1 },
    shadow: cardShadow(),
  });
}

// 1. Open
{
  const slide = pres.addSlide();
  slide.background = { color: navy };
  slide.addText("SYNTHETIC POC  ·  NOT A DEPLOYMENT", {
    x: 0.6, y: 1.35, w: 12, h: 0.32,
    fontFace: "Calibri", fontSize: 14, color: "C5D0DA", margin: 0,
  });
  slide.addText("Paperlane lakehouse\ncustomer demonstration", {
    x: 0.6, y: 1.8, w: 10.5, h: 1.8,
    fontFace: "Georgia", fontSize: 40, color: "FFFFFF", margin: 0,
  });
  slide.addText("Orders, events, a medallion layout, and a refund score that is allowed to lose.", {
    x: 0.6, y: 3.8, w: 10, h: 0.4,
    fontFace: "Calibri", fontSize: 18, color: "C5D0DA", margin: 0,
  });
  const facts = [
    ["Dataset\npaperlane-v1-fixed-18", ink],
    ["Organization\nSYN-ORG-PAPERLANE", ink],
    ["Decision\nNO-GO", deny],
  ];
  facts.forEach((fact, index) => {
    const x = 0.6 + index * 4.2;
    panel(slide, x, 4.6, 3.95, 1.2);
    slide.addText(fact[0], {
      x: x + 0.2, y: 4.75, w: 3.55, h: 0.9,
      fontFace: "Calibri", fontSize: 16, color: fact[1], margin: 0,
    });
  });
  slide.addNotes("Open by saying the notice out loud: SYNTHETIC_POC_NOT_A_DEPLOYMENT. Paperlane is not a customer extract. This laptop is not a Databricks workspace. The decision on the slide is NO-GO and it stays there for the whole meeting. About one minute.");
}

// 2. Problem
{
  const slide = pres.addSlide();
  header(slide, "01  ·  Problem", "Refund review is still a spreadsheet");
  panel(slide, 0.5, 1.55, 7.4, 5.2);
  slide.addText("What they asked for", {
    x: 0.75, y: 1.75, w: 6.9, h: 0.35,
    fontFace: "Georgia", fontSize: 20, color: navy, margin: 0,
  });
  slide.addText([
    { text: "Orders and site events arrive as files, including a captured topic.", options: { bullet: true, breakLine: true } },
    { text: "Keep the raw files, then a clean table an analyst can trust.", options: { bullet: true, breakLine: true } },
    { text: "Publish daily category revenue.", options: { bullet: true, breakLine: true } },
    { text: "Score refunds, and keep the score only if it beats a majority baseline.", options: { bullet: true } },
  ], {
    x: 0.75, y: 2.3, w: 6.9, h: 2.4,
    fontFace: "Calibri", fontSize: 18, color: ink, paraSpaceAfter: 10,
  });
  slide.addText("Inkwell exists only so a cross-tenant read can be refused.", {
    x: 0.75, y: 5.4, w: 6.9, h: 0.7,
    fontFace: "Calibri", fontSize: 16, color: muted, margin: 0,
  });
  const people = [
    ["Leta", "Analyst", "Paperlane"],
    ["Omar", "Engineer", "Paperlane"],
    ["Prue", "Analyst", "Inkwell"],
  ];
  people.forEach((person, index) => {
    const y = 1.55 + index * 1.75;
    panel(slide, 8.15, y, 4.65, 1.6);
    slide.addText(person[0], {
      x: 8.4, y: y + 0.18, w: 4.2, h: 0.4,
      fontFace: "Georgia", fontSize: 22, color: navy, margin: 0,
    });
    slide.addText(person[1] + "  ·  " + person[2], {
      x: 8.4, y: y + 0.7, w: 4.2, h: 0.4,
      fontFace: "Calibri", fontSize: 16, color: index === 2 ? deny : teal, margin: 0,
    });
  });
  footer(slide, "SYN-USER-LETA   SYN-USER-OMAR   SYN-USER-PRUE");
  slide.addNotes("One minute. The prospect wants a medallion, a daily number, and a model that is allowed to lose. Prue is not a second implementation. She is the stop.");
}

// 3. Medallion
{
  const slide = pres.addSlide();
  header(slide, "02  ·  Layout", "Bronze keeps it. Silver cleans it. Gold publishes it.");
  const layers = [
    ["Bronze", "Raw files", "240 clean orders, 8 dirty orders, 3 Inkwell orders, and the duplicate events."],
    ["Silver", "Clean and validate", "240 Paperlane orders. Email is dropped. Inkwell ids are absent. 382 events."],
    ["Gold", "Analytics and the score", "16 daily category rows. Features for the refund comparison. Analyst-facing."],
  ];
  layers.forEach((layer, index) => {
    const x = 0.5 + index * 4.2;
    panel(slide, x, 1.7, 3.95, 3.7);
    slide.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.7, w: 3.95, h: 0.12, fill: { color: teal },
    });
    slide.addText(layer[0], {
      x: x + 0.25, y: 2.05, w: 3.45, h: 0.5,
      fontFace: "Georgia", fontSize: 26, color: navy, margin: 0,
    });
    slide.addText(layer[1], {
      x: x + 0.25, y: 2.65, w: 3.45, h: 0.4,
      fontFace: "Calibri", fontSize: 16, color: teal, margin: 0,
    });
    slide.addText(layer[2], {
      x: x + 0.25, y: 3.25, w: 3.45, h: 1.8,
      fontFace: "Calibri", fontSize: 16, color: ink, margin: 0,
    });
  });
  footer(slide, "Ten data-quality failures stay in the quarantine count. They are not deleted from the story.");
  slide.addNotes("Two minutes. Point at the diagram in the README if the room can see the repo. Bronze is retain. Silver is the trust boundary. Gold is what Leta is allowed to select.");
}

// 4. Quality
{
  const slide = pres.addSlide();
  header(slide, "03  ·  Data quality", "Ten failures. Two of each reason.");
  panel(slide, 0.5, 1.6, 4.3, 3.5);
  slide.addText("10", {
    x: 0.7, y: 1.9, w: 3.9, h: 1.4,
    fontFace: "Georgia", fontSize: 72, color: warn, margin: 0,
  });
  slide.addText("quarantined rows\nnot removed from bronze", {
    x: 0.7, y: 3.25, w: 3.9, h: 0.7,
    fontFace: "Calibri", fontSize: 18, color: ink, margin: 0,
  });
  slide.addText("Silver still holds 240 orders.\nInkwell rows in silver: 0.", {
    x: 0.7, y: 4.05, w: 3.9, h: 0.8,
    fontFace: "Calibri", fontSize: 16, color: muted, margin: 0,
  });
  const reasons = [
    ["negative_amount", "2"],
    ["missing_customer", "2"],
    ["future_timestamp", "2"],
    ["unknown_currency", "2"],
    ["duplicate_event", "2"],
  ];
  slide.addTable(
    [
      [
        { text: "Reason", options: { fill: { color: navy }, color: "FFFFFF", bold: true } },
        { text: "Count", options: { fill: { color: navy }, color: "FFFFFF", bold: true } },
      ],
      ...reasons.map((row) => [
        { text: row[0], options: { fill: { color: card }, color: ink } },
        { text: row[1], options: { fill: { color: card }, color: ink, align: "right" } },
      ]),
    ],
    {
      x: 5.1, y: 1.7, w: 7.6, h: 3.2,
      colW: [5.2, 2.4],
      fontFace: "Calibri",
      fontSize: 16,
      rowH: [0.48, 0.52, 0.52, 0.52, 0.52, 0.52],
      border: [{ pt: 0.5, color: stroke }, { pt: 0.5, color: stroke }, { pt: 0.5, color: stroke }, { pt: 0.5, color: stroke }],
      valign: "middle",
    }
  );
  footer(slide, "Dataset paperlane-v1-fixed-18");
  slide.addNotes("One minute. Read two reasons aloud: a future timestamp and a duplicate event. The other three are amount, customer, and currency. Silver is 240. Email is not on the silver columns.");
}

// 5. Delta
{
  const slide = pres.addSlide();
  header(slide, "04  ·  Delta", "MERGE adds a column and corrects order 10");
  const steps = [
    ["1", "First write", "Orders 1–180. No gift-wrap column yet."],
    ["2", "Second batch", "Order 10 becomes 100 cents. Orders 181–240 arrive with gift wrap."],
    ["3", "After MERGE", "240 orders. Order 1 has no gift wrap. Order 240 does. History has WRITE and MERGE."],
  ];
  steps.forEach((step, index) => {
    const y = 1.55 + index * 1.7;
    panel(slide, 0.5, y, 12.3, 1.55);
    slide.addText(step[0], {
      x: 0.75, y: y + 0.35, w: 0.7, h: 0.7,
      fontFace: "Georgia", fontSize: 28, color: teal, margin: 0,
    });
    slide.addText(step[1], {
      x: 1.7, y: y + 0.22, w: 10.6, h: 0.4,
      fontFace: "Georgia", fontSize: 20, color: navy, margin: 0,
    });
    slide.addText(step[2], {
      x: 1.7, y: y + 0.72, w: 10.6, h: 0.5,
      fontFace: "Calibri", fontSize: 18, color: ink, margin: 0,
    });
  });
  footer(slide, "The stream proof is separate: availableNow moves 180 rows to 240 when the second file lands. No broker.");
  slide.addNotes("Two minutes. This merge is not the training set. The model uses the uncorrected generated orders, and amount is not a feature. The stream is availableNow on local JSON, not a Kafka cluster.");
}

// 6. Access
{
  const slide = pres.addSlide();
  header(slide, "05  ·  Access", "Gold is for Paperlane analysts. Bronze is not.");
  const grants = [
    [ok, "Leta", "Can select gold daily revenue and order features. Cannot select bronze."],
    [teal, "Omar", "Can select bronze, silver, and gold. Can modify Paperlane gold."],
    [deny, "Prue", "Inkwell analyst. Denied on Paperlane objects, including gold."],
  ];
  grants.forEach((item, index) => {
    const x = 0.5 + index * 4.2;
    panel(slide, x, 1.8, 3.95, 3.5);
    slide.addShape(pres.shapes.OVAL, {
      x: x + 0.25, y: 2.1, w: 0.38, h: 0.38, fill: { color: item[0] },
    });
    slide.addText(item[1], {
      x: x + 0.8, y: 2.08, w: 2.8, h: 0.42,
      fontFace: "Georgia", fontSize: 24, color: navy, margin: 0,
    });
    slide.addText(item[2], {
      x: x + 0.25, y: 2.8, w: 3.45, h: 2.6,
      fontFace: "Calibri", fontSize: 18, color: ink, margin: 0,
    });
  });
  footer(slide, "resources/unity_catalog.sql was not applied. Fixture tokens stay inside this process.");
  slide.addNotes("One and a half minutes. The SQL file is role-named. The local enforcer is stricter: any other tenant is denied before the role check. Say that the file was not executed on Unity Catalog.");
}

// 7. SQL
{
  const slide = pres.addSlide();
  header(slide, "06  ·  Spark SQL", "Partitioning did not win this run");
  slide.addTable(
    [
      [
        { text: "Layout", options: { fill: { color: navy }, color: "FFFFFF", bold: true } },
        { text: "p50 seconds", options: { fill: { color: navy }, color: "FFFFFF", bold: true } },
        { text: "p95 seconds", options: { fill: { color: navy }, color: "FFFFFF", bold: true } },
      ],
      [
        { text: "Partitioned by sale_date", options: { fill: { color: card }, color: ink } },
        { text: "0.4407844999950612", options: { fill: { color: card }, color: ink } },
        { text: "0.5313135000033071", options: { fill: { color: card }, color: ink } },
      ],
      [
        { text: "Unpartitioned scan", options: { fill: { color: "E7F2F2" }, color: ink } },
        { text: "0.397024899997632", options: { fill: { color: "E7F2F2" }, color: ink, bold: true } },
        { text: "0.455856100001256", options: { fill: { color: "E7F2F2" }, color: ink } },
      ],
    ],
    {
      x: 0.5, y: 1.6, w: 7.3, h: 2.5,
      colW: [3.1, 2.3, 1.9],
      fontFace: "Calibri",
      fontSize: 13,
      border: [
        { pt: 0.5, color: stroke },
        { pt: 0.5, color: stroke },
        { pt: 0.5, color: stroke },
        { pt: 0.5, color: stroke },
      ],
      valign: "middle",
    }
  );
  panel(slide, 0.5, 4.35, 7.3, 2.4);
  slide.addText("40,000 rows · 40 repeats · Spark 3.5.6\nEngine spark-sql-local. SQL warehouse not-run.\nSame predicate: sale_date = 2026-03-08.", {
    x: 0.75, y: 4.6, w: 6.9, h: 1.9,
    fontFace: "Calibri", fontSize: 16, color: ink, margin: 0,
  });
  slide.addChart(pres.charts.BAR, [
    {
      name: "p50",
      labels: ["Partitioned", "Unpartitioned"],
      values: [0.4407844999950612, 0.397024899997632],
    },
  ], {
    x: 8.0, y: 1.6, w: 4.8, h: 5.1,
    barDir: "bar",
    chartColors: ["0F6E6E"],
    showLegend: false,
    showValue: false,
    chartArea: { fill: { color: card } },
    catAxisLabelColor: ink,
    valAxisLabelColor: muted,
    valAxisMaxVal: 0.8,
    valGridLine: { color: stroke, size: 0.5 },
    catGridLine: { style: "none" },
  });
  footer(slide, "i7-1185G7 · 4 cores · 8 logical · free 8961196 KB of 32916868 KB");
  slide.addNotes("Two minutes. Read both p50s. The partitioned number is higher. Do not say pruning helped. Do not mention Photon. The hardware line is the CIM read from this benchmark, not an earlier repo.");
}

// 8. Model
{
  const slide = pres.addSlide();
  header(slide, "07  ·  Refund score", "The logistic model does not clear the bar");
  panel(slide, 0.5, 1.6, 4.0, 3.3);
  panel(slide, 4.7, 1.6, 4.0, 3.3);
  panel(slide, 8.9, 1.6, 3.9, 3.3);
  slide.addText("0.0", {
    x: 0.7, y: 1.85, w: 3.6, h: 1.1,
    fontFace: "Georgia", fontSize: 54, color: navy, margin: 0,
  });
  slide.addText("Majority F1", {
    x: 0.7, y: 3.15, w: 3.6, h: 0.4,
    fontFace: "Calibri", fontSize: 18, color: muted, margin: 0,
  });
  slide.addText("Refund class on the\ntraining majority.", {
    x: 0.7, y: 3.65, w: 3.6, h: 0.8,
    fontFace: "Calibri", fontSize: 15, color: ink, margin: 0,
  });
  slide.addText("0.0", {
    x: 4.9, y: 1.85, w: 3.6, h: 1.1,
    fontFace: "Georgia", fontSize: 54, color: navy, margin: 0,
  });
  slide.addText("Logistic F1", {
    x: 4.9, y: 3.15, w: 3.6, h: 0.4,
    fontFace: "Calibri", fontSize: 18, color: muted, margin: 0,
  });
  slide.addText("False-positive rate 0.0.\nNo score reached 0.5.", {
    x: 4.9, y: 3.65, w: 3.6, h: 0.8,
    fontFace: "Calibri", fontSize: 15, color: ink, margin: 0,
  });
  slide.addText("majority", {
    x: 9.1, y: 2.05, w: 3.5, h: 0.8,
    fontFace: "Georgia", fontSize: 28, color: ok, margin: 0,
  });
  slide.addText("Recommendation", {
    x: 9.1, y: 3.0, w: 3.5, h: 0.4,
    fontFace: "Calibri", fontSize: 18, color: muted, margin: 0,
  });
  slide.addText("Rule matched choose().", {
    x: 9.1, y: 3.55, w: 3.5, h: 0.6,
    fontFace: "Calibri", fontSize: 15, color: ink, margin: 0,
  });
  panel(slide, 0.5, 5.1, 12.3, 1.7);
  slide.addText("Frozen before the score: margin 0.05, false-positive cap 0.20, threshold 0.5, C = 1.0, no class weight. Those knobs were not turned after the zeros.", {
    x: 0.75, y: 5.4, w: 11.8, h: 1.1,
    fontFace: "Calibri", fontSize: 18, color: ink, margin: 0,
  });
  footer(slide, "Holdout is n >= 181, 60 orders, 4 refunds. MLflow file store. Two runs: majority and logistic.");
  slide.addNotes("Two minutes. The honest recommendation is majority. Do not offer to lower the threshold in the room. The fit printed an iprint solver warning and still returned coefficients. Mention the warning if someone asks why the log is noisy. Do not retune.");
}

// 9. Boundaries
{
  const slide = pres.addSlide();
  header(slide, "08  ·  Boundary", "What ran, and what was not contacted");
  panel(slide, 0.5, 1.55, 6.0, 4.6);
  panel(slide, 6.8, 1.55, 6.0, 4.6);
  slide.addText("Ran on this machine", {
    x: 0.75, y: 1.75, w: 5.5, h: 0.4,
    fontFace: "Georgia", fontSize: 20, color: ok, margin: 0,
  });
  slide.addText([
    { text: "Synthetic generator and quality checks", options: { bullet: true, breakLine: true } },
    { text: "Local Spark 3.5.6 Delta MERGE and availableNow", options: { bullet: true, breakLine: true } },
    { text: "Spark SQL timings in benchmarks/latest.json", options: { bullet: true, breakLine: true } },
    { text: "In-process grants and a local MLflow file store", options: { bullet: true, breakLine: true } },
    { text: "pytest, ruff, and mypy", options: { bullet: true } },
  ], {
    x: 0.75, y: 2.35, w: 5.5, h: 3.8,
    fontFace: "Calibri", fontSize: 16, color: ink, paraSpaceAfter: 8,
  });
  slide.addText("Not contacted", {
    x: 7.05, y: 1.75, w: 5.5, h: 0.4,
    fontFace: "Georgia", fontSize: 20, color: deny, margin: 0,
  });
  slide.addText([
    { text: "Databricks workspace and the CLI", options: { bullet: true, breakLine: true } },
    { text: "Unity Catalog and Lakeflow services", options: { bullet: true, breakLine: true } },
    { text: "SQL warehouse and Photon", options: { bullet: true, breakLine: true } },
    { text: "Kafka broker and cloud buckets", options: { bullet: true, breakLine: true } },
    { text: "A hosted model. Tokens 0. Price none.", options: { bullet: true } },
  ], {
    x: 7.05, y: 2.35, w: 5.5, h: 3.8,
    fontFace: "Calibri", fontSize: 16, color: ink, paraSpaceAfter: 8,
  });
  footer(slide, "Deployment decision NO-GO");
  slide.addNotes("One minute. If someone asks for a workspace tour, say those services were not-run. The asset bundle file says it was not run.");
}

// 10. Close
{
  const slide = pres.addSlide();
  header(slide, "09  ·  Close", "Accept the baseline. Do not deploy.");
  const closes = [
    ["16", "refunds, 4 in the holdout"],
    ["majority", "the published recommendation"],
    ["NO-GO", "until a real workspace is measured"],
  ];
  closes.forEach((item, index) => {
    const x = 0.5 + index * 4.2;
    panel(slide, x, 1.8, 3.95, 2.7);
    slide.addText(item[0], {
      x: x + 0.2, y: 2.1, w: 3.55, h: 1.1,
      fontFace: "Georgia", fontSize: index === 0 ? 48 : 28, color: index === 2 ? deny : navy, margin: 0,
    });
    slide.addText(item[1], {
      x: x + 0.2, y: 3.25, w: 3.55, h: 0.9,
      fontFace: "Calibri", fontSize: 18, color: ink, margin: 0,
    });
  });
  slide.addText("Walk the rest from docs/demo-script.md. The static report is docs/dashboard.html.", {
    x: 0.5, y: 5.4, w: 12.3, h: 0.8,
    fontFace: "Calibri", fontSize: 18, color: muted, margin: 0,
  });
  footer(slide, "Jatinder Singh  ·  MIT 2026  ·  Price none");
  slide.addNotes("One minute. Restate NO-GO. Offer the demo script if they want the file-by-file path. Do not promise a deployment date. Stop.");
}

pres.writeFile({ fileName: "F:/agy/github/databricks-lakehouse-customer-poc/docs/presentation/paperlane-poc.pptx" })
  .then(() => console.log("wrote pptx"))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
