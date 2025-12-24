
let pipelineExecuted = false;
let requestToken = 0;
let evennessData = null;
let neatnessData = null;
let currentView = null;

const HIDE_KEYWORDS = ["time", "date", "path", "output_image_path"];

// ================= EXECUTE PIPELINE =================
function executePipeline() {
    // Disable all buttons during execution
    setButtons({
        evenness: false,
        neatness: false,
        execute: false,
        home: false,
        print: false
    });

    showStatus("Processing...");

    fetch("/execute", { method: "POST" })
        .then(res => res.json())
        .then(() => {
            pipelineExecuted = true;
            showStatus("Execution completed.");

            // 🔥 WAIT for both CSV files to be available
            Promise.all([
                new Promise(resolve =>
                    waitForCSV("evenness", csv => resolve({ type: "evenness", csv }))
                ),
                new Promise(resolve =>
                    waitForCSV("neatness", csv => resolve({ type: "neatness", csv }))
                )
            ])
            .then(results => {
                results.forEach(r => {
                    if (r.type === "evenness") {
                        evennessData = parseCSV(r.csv);
                    }
                    if (r.type === "neatness") {
                        neatnessData = parseCSV(r.csv);
                    }
                });

                currentView = "evenness";
                renderFromMemory();

                // Enable interaction buttons AFTER data is ready
                setButtons({
                    evenness: true,
                    neatness: true,
                    execute: false,   // stay disabled until Home
                    home: true,
                    print: true
                });
            });
        })
        .catch(err => {
            console.error(err);
            showStatus("Execution failed");

            // Allow retry
            setButtons({
                evenness: false,
                neatness: false,
                execute: true,
                home: false,
                print: false
            });
        });
}


function waitForCSV(type, callback) {
    fetch(`/csv/${type}`)
        .then(res => {
            if (res.status === 204) {
                setTimeout(() => waitForCSV(type, callback), 1000); // ⏳ wait
                return null;
            }
            return res.text();
        })
        .then(text => {
            if (!text) return;
            callback(text);
        });
}


function parseCSV(text) {
    return text
        .trim()
        .split("\n")
        .map(row => row.split(","));
}


function goHome() {
    saveCurrentEdits();  // 🔥 capture latest edits

    fetch("/home", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            evenness: evennessData.map(r => r.join(",")).join("\n"),
            neatness: neatnessData.map(r => r.join(",")).join("\n")
        })
    })
    .then(() => {
        evennessData = null;
        neatnessData = null;
        currentView = null;

        clearTable();
        showStatus("");

        setButtons({
            evenness: false,
            neatness: false,
            execute: true,
            home: false,
            print: false
        });
    });
}



function printTable() {
    if (!pipelineExecuted) return;
    window.print();
}


function clearTable() {
    const thead = document.querySelector("#csvTable thead");
    const tbody = document.querySelector("#csvTable tbody");

    thead.innerHTML = "<tr><th>Result</th></tr>";
    tbody.innerHTML = "";
}


// ================= LOAD CSV =================
function loadCSV(type) {
    saveCurrentEdits();   // 🔥 persist edits before switching
    currentView = type;
    renderFromMemory();
}

function renderFromMemory() {
    if (currentView === "evenness" && evennessData) {
        renderTable(evennessData);
    }
    if (currentView === "neatness" && neatnessData) {
        renderTable(neatnessData);
    }
}


function saveCurrentEdits() {
    if (!currentView) return;

    const table = document.getElementById("csvTable");
    let updated = [];

    for (let r of table.rows) {
        let row = [];
        for (let c of r.cells) {
            row.push(c.innerText.trim());
        }
        updated.push(row);
    }

    if (currentView === "evenness") evennessData = updated;
    if (currentView === "neatness") neatnessData = updated;
}




// ================= HELPERS =================
function setButtons(state) {
    document.getElementById("btnEvenness").disabled = !state.evenness;
    document.getElementById("btnNeatness").disabled = !state.neatness;
    document.getElementById("btnExecute").disabled = !state.execute;
    document.getElementById("btnHome").disabled = !state.home;
    document.getElementById("btnPrint").disabled = !state.print;
}


function shouldHide(header) {
    return HIDE_KEYWORDS.some(k => header.toLowerCase().includes(k));
}

function disableButtons(state) {
    document.querySelectorAll("button").forEach(btn => btn.disabled = state);
}

function showStatus(msg) {
    let status = document.getElementById("status");
    if (!status) {
        status = document.createElement("div");
        status.id = "status";
        status.style.padding = "5px";
        status.style.fontWeight = "bold";
        document.querySelector(".content").prepend(status);
    }
    status.textContent = msg;
}

// ================= TABLE RENDER =================
function renderZeroTable() {
    const thead = document.querySelector("#csvTable thead");
    const tbody = document.querySelector("#csvTable tbody");

    thead.innerHTML = "<tr><th>Result</th></tr>";
    showStatus("");
}

function renderTable(data) {
    const thead = document.querySelector("#csvTable thead");
    const tbody = document.querySelector("#csvTable tbody");

    thead.innerHTML = "";
    tbody.innerHTML = "";

    const headers = data[0];
    const visibleCols = headers
        .map((h, i) => ({ h, i }))
        .filter(c => !shouldHide(c.h))
        .map(c => c.i);

    const headerRow = document.createElement("tr");
    visibleCols.forEach(i => {
        const th = document.createElement("th");
        th.textContent = headers[i];
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);

    for (let r = 1; r < data.length; r++) {
        const tr = document.createElement("tr");
        visibleCols.forEach(i => {
            const td = document.createElement("td");
            td.textContent = data[r][i] || "";
            td.contentEditable = "true";   // 🔥 editable cell
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    }
}

function getTableCSV() {
    const table = document.getElementById("csvTable");
    let csv = [];

    for (let row of table.rows) {
        let cols = [];
        for (let cell of row.cells) {
            cols.push(cell.innerText.replace(/,/g, "")); // avoid CSV break
        }
        csv.push(cols.join(","));
    }

    return csv.join("\n");
}


function printTable() {
    window.print();
}




// ================= INITIAL STATE =================
setButtons({
    evenness: false,
    neatness: false,
    execute: true,   // user must be able to start
    home: false,
    print: false
});

clearTable();

renderZeroTable();
