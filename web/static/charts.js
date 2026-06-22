async function loadChart(endpoint, canvasId, label, color) {
    const res = await fetch(endpoint);
    const data = await res.json();

    new Chart(document.getElementById(canvasId), {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{
                label: label,
                data: data.values,
                backgroundColor: color,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: "#aaa" }, grid: { color: "#2a2d3e" } },
                y: { ticks: { color: "#aaa" }, grid: { color: "#2a2d3e" } }
            }
        }
    });
}
async function actualizar() {
    const btn = document.getElementById("btnActualizar");
    const msg = document.getElementById("msgActualizar");

    btn.disabled = true;
    btn.innerHTML = "⏳ Scrapeando...";
    msg.style.color = "#888";
    msg.textContent = "Esto puede tardar unos segundos...";

    try {
        const res = await fetch("/api/actualizar", { method: "POST" });
        const data = await res.json();

        if (data.status === "ok") {
            msg.style.color = "#34d399";
            msg.textContent = "✅ " + data.mensaje;
            setTimeout(() => location.reload(), 1500);
        } else {
            msg.style.color = "#f87171";
            msg.textContent = "❌ " + data.mensaje;
        }
    } catch (e) {
        msg.style.color = "#f87171";
        msg.textContent = "❌ Error de conexión";
    } finally {
        btn.disabled = false;
        btn.innerHTML = "🔄 Actualizar datos";
    }
}
loadChart("/api/tecnologias", "chartTecnologias", "Menciones", "#4f8ef7");
loadChart("/api/empresas", "chartEmpresas", "Ofertas", "#34d399");